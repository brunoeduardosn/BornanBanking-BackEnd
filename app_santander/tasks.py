import json
import subprocess
from celery import shared_task
from django.db import connection
import time
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.template.loader import render_to_string
import base64
import requests
from django.core.files.base import ContentFile
from weasyprint import HTML, CSS
from datetime import datetime, timedelta
from app_banks.models import Bank, Billing
from app_core.utils import convert_date_to_str, convert_decimal_to_str, remove_empty_fields
from app_santander.models import SantanderBillingLog, SantanderConfiguration

@shared_task
def solicitar_token(enviroment, client_id, client_secret):
    print(f'Solicitou Token para o ambiente {enviroment}')
    if enviroment == 'sandbox':
        token_url = "https://trust-sandbox.api.santander.com.br/auth/oauth/v2/token"
    elif enviroment == 'production':
        token_url = "https://trust.api.santander.com.br/auth/oauth/v2/token"
    else:
        return JsonResponse({'error': 'Invalid environment'}, status=400)
    
    token_payload = f'client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials'
    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    cert_path = './cetificados/certificado.crt'
    key_path = './cetificados/chave.key'

    try:
        token_response = requests.post(token_url, headers=token_headers, data=token_payload, cert=(cert_path, key_path))
        token_response_data = token_response.json()
        access_token = token_response_data.get('access_token')
        if not access_token:
            return JsonResponse({'error': 'Failed to obtain access token'}, status=500)
        
        return access_token
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@shared_task
def create_workspace(tenant_id, bank_id):
    print(f'Criando workspace para o banco {bank_id}')
    bank = Bank.objects.get(id=bank_id, tenant_id=tenant_id)
    environment = bank.environment
    description = bank.name
    
    configuration = SantanderConfiguration.objects.get(bank_id=bank_id, tenant_id=tenant_id)
    type = configuration.type
    covenant = configuration.covenant
    webhookURL = configuration.webhookURL
    bankSlipBillingWebhookActive = configuration.bankSlipBillingWebhookActive
    pixBillingWebhookActive = configuration.pixBillingWebhookActive
    
    if environment == 'sandbox':
        workspace_url = "https://trust-sandbox.api.santander.com.br/collection_bill_management/v2/workspaces"
    elif environment == 'production':
        workspace_url = "https://trust.api.santander.com.br/collection_bill_management/v2/workspaces"
    else:
        return JsonResponse({'error': 'Invalid environment'}, status=400)
    
    access_token = solicitar_token(bank.environment, configuration.client_id, configuration.client_secret)
    
    workspace_payload = json.dumps({
        "type": type,
        "covenants": [
            {
                "code": covenant
            }
        ],
        "description": description,
        "bankSlipBillingWebhookActive": bankSlipBillingWebhookActive,
        "pixBillingWebhookActive": pixBillingWebhookActive,
        "webhookURL": webhookURL
    })
    
    print(f'Payload: {workspace_payload}')
    
    workspace_headers = {
        'X-Application-Key': configuration.client_id,
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    try:
        workspace_response = requests.post(workspace_url, headers=workspace_headers, data=workspace_payload)
        print(f'Workspace criado com sucesso: {workspace_response.json()}')
        
        if workspace_response.status_code == 201:
            workspace_data = workspace_response.json()
            workspace_id = workspace_data.get('id')
            print(f'Workspace ID: {workspace_id}')
            if workspace_id:
                configuration.workspace = workspace_id
                configuration.save()
                return JsonResponse({'message': 'Workspace criado com sucesso', 'workspace_id': workspace_id}, status=201)
            else:
                return JsonResponse({'error': 'Workspace ID not found in response'}, status=500)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)


@shared_task
def billing_register(tenant_id, bank_id, billing_id, operation):
    print(f'Atualizando boleto {billing_id}')
    log_santander = SantanderBillingLog.objects.create(
        tenant_id=tenant_id,
        billing_id=billing_id,
        status='pending',
        type_integration=operation
    )
    try:
        bank = Bank.objects.get(id=bank_id, tenant_id=tenant_id)
        configuration = SantanderConfiguration.objects.get(bank_id=bank_id, tenant_id=tenant_id)
        billing = Billing.objects.get(id=billing_id, tenant_id=tenant_id)
        
        environment = bank.environment
            
        if environment == 'sandbox':
            billing_url = f"https://trust-sandbox.api.santander.com.br/collection_bill_management/v2/workspaces/{configuration.workspace}/bank_slips"
            nsucode = 'TST' + billing.bank_number
            environment_type = 'TESTE'
        elif environment == 'production':
            billing_url = f"https://trust.api.santander.com.br/collection_bill_management/v2/workspaces/{configuration.workspace}/bank_slips"
            nsucode = billing.bank_number
            environment_type = 'PRODUCAO'
        else:
            print('Invalid environment')
            return
        
        access_token = solicitar_token(bank.environment, configuration.client_id, configuration.client_secret)        
        billing_payload = None  # Inicializar a variável billing_payload
        
        if operation == 'register':
            print('Iniciando Payload: Registrando boleto....')
            status_billing = 'registered'
            discount_type = configuration.discount_type
            discount_one_value = 0
            discount_one_limitdate = ''
            discount_two_value = 0
            discount_two_limitdate = ''
            discount_three_value = 0
            discount_three_limitdate = ''
            
            if discount_type == 'ISENTO':
                discount_one_value = 0
                discount_one_limitdate = ''
                discount_two_value = 0
                discount_two_limitdate = ''
                discount_three_value = 0
                discount_three_limitdate = ''
            
            elif discount_type == 'VALOR_DATA_FIXA':
                discount_one_value = configuration.discountone_value
                discount_one_limitdate = billing.due_date - timedelta(days=configuration.discountone_limitdate)
                discount_two_value = configuration.discounttwo_value
                discount_two_limitdate = billing.due_date - timedelta(days=configuration.discounttwo_limitdate)
                discount_three_value = configuration.discountthree_value
                discount_three_limitdate = billing.due_date - timedelta(days=configuration.discountthree_limitdate)
                
            elif discount_type == 'VALOR_DIA_CORRIDO' or discount_type == 'VALOR_DIA_UTIL':
                discount_one_value = configuration.discountone_value
                discount_one_limitdate = ''
                discount_two_value = configuration.discounttwo_value
                discount_two_limitdate = ''
                discount_three_value = configuration.discountthree_value
                discount_three_limitdate = ''
            
            billing_payload = {
                # Ambiente
                "environment": environment_type,
                
                "covenantCode": configuration.covenant,
                # Dados do boleto
                "nsuCode": nsucode, # Número único do boleto
                "nsuDate": datetime.now().strftime('%Y-%m-%d'), # Data de emissão do boleto
                "bankNumber": billing.bank_number, # Nosso número do banco
                "clientNumber": billing.document, # Nosso número do cliente
                
                # Dados de valores e vencimento
                "documentKind": billing.document_kind,
                "issueDate": datetime.now().strftime('%Y-%m-%d'), # Data de emissão
                "dueDate": billing.due_date.strftime('%Y-%m-%d'), # Data de vencimento
                "nominalValue": str(billing.nominal_value), # Valor nominal
                "deductionValue": billing.deduction_value, # Valor de desconto
                
                # Dados de Juros, Multa e Protesto
                "finePercentage": configuration.finepercent, # Porcentagem de multa
                "fineQuantityDays": configuration.finequantitydays, # Data limite para multa
                "interestPercentage": configuration.interestpercent, # Porcentagem de juros
                "protestType": configuration.protest_type, # Tipo de protesto
                "protestQuantityDays": configuration.protest_days, # Dias para protesto
            
                # Dados de pagamento
                "paymentType": configuration.payment_type,
                "parcelsQuantity": configuration.parcels_quantity,
                "writeOffQuantityDays": configuration.writeoff_quantity_days,
                "valueType": configuration.value_type,
                "minValueOrPercentage": configuration.min_value_or_percentage,
                "maxValueOrPercentage": configuration.max_value_or_percentage,
                
                # Dados do pagador
                "payer": {
                    "name": billing.payer_name,
                    "documentType": billing.payer_document_type,
                    "documentNumber": billing.payer_document_number,
                    "address": billing.payer_address,
                    "neighborhood": billing.payer_neighborhood,
                    "city": billing.payer_city,
                    "state": billing.payer_state,
                    "zipCode": billing.payer_zip_code
                },
                
                # Dados do beneficiário
                "beneficiary": {
                    "name": billing.beneficiary_name,
                    "documentType": billing.beneficiary_document_type,
                    "documentNumber": billing.beneficiary_document_number
                },
                
                # Dados do desconto especial
                "discount": {
                    "type": configuration.discount_type,
                    "discountOne": {
                        "value": discount_one_value,
                        "limitDate": discount_one_limitdate
                        },
                    "discountTwo": {
                        "value": discount_two_value,
                        "limitDate": discount_two_limitdate
                        },
                    "discountThree": {
                        "value": discount_three_value,
                        "limitDate": discount_three_limitdate
                        }
                },
                
                "messages": configuration.messages,
                
                # Dados de PIX Boleto
                "key":{
                    "type": configuration.key_type,
                    "dictKey": configuration.key_dictkey,
                    "txId": configuration.txid
                },
                
            }
        
        elif operation == 'update':
            status_billing = 'registered'
            billing_payload = {
                "covenantCode": configuration.covenant,
                "bankNumber": billing.bank_number,
                "clientNumber": billing.document,
                "dueDate": billing.due_date.strftime('%Y-%m-%d'), # Pode antecipar ou prorrogar a data de vencimento
                
                # Dados de Juros, Multa e Protesto
                "protestType": billing.protest_type, # Tipo de protesto
                "deductionValue": billing.deduction_value, # Valor de desconto
                "finePercentage": billing.fine_value, # Porcentagem de multa 
                "fineDate": billing.due_date + timedelta(days=configuration.finequantitydays), # Data limite para multa
                "interest":{
                    "interestPercentage": billing.interest_value, # Porcentagem de juros
                }
            }

        elif operation == 'canceled':
            status_billing = 'canceled'
            billing_payload = {
                "covenantCode": configuration.covenant,
                "bankNumber": billing.bank_number,
                "operation": "BAIXAR"
                }
            
        elif operation == 'protested': # Apenas para boletos vencidos
            status_billing = 'protest'
            billing_payload = {
                "covenantCode": configuration.covenant,
                "bankNumber": billing.bank_number,
                "operation": "PROTESTAR"
                }
        
        elif operation == 'cancel_protest':
            status_billing = 'registered'
            billing_payload = {
                "covenantCode": configuration.covenant,
                "bankNumber": billing.bank_number,
                "operation": "CANCELAR_PROTESTO"
                }
        
        if billing_payload is None:
            print('Operação inválida')
            return
        
        billing_headers = {
            'X-Application-Key': configuration.client_id,
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        
        billing_payload = remove_empty_fields(billing_payload)
        billing_payload = convert_decimal_to_str(billing_payload)  # Converter Decimals para strings
        billing_payload = convert_date_to_str(billing_payload)  # Converter dates para strings

        billing_payload_json = json.dumps(billing_payload)
        log_santander.payload = billing_payload_json
        log_santander.save()
        #print(f'Payload: {billing_payload_json}')
        
        if operation == 'registrar':
            billing_response = requests.post(billing_url, headers=billing_headers, data=billing_payload_json)
        else:
            billing_response = requests.patch(billing_url, headers=billing_headers, data=billing_payload_json)
            
        #print(f'Retorno: {billing_response.json()}')
        #print(f'Status Code: {billing_response.status_code}')
        
        if (billing_response.status_code == 201 or billing_response.status_code == 200) and operation == 'registrar':
            billing_data = billing_response.json()
            billing.status = status_billing
            billing.barcode = billing_data.get('barcode')
            billing.digitableline = billing_data.get('digitableLine')
            billing.entrydate = billing_data.get('entryDate')
            billing.qrcodepix = billing_data.get('qrCodePix')
            billing.qrcodeurl = billing_data.get('qrCodeUrl')
            billing.save()
            log_santander.message = 'Finalizado com sucesso'
            log_santander.response = billing_response.json()
            log_santander.status = 'success'
            log_santander.save()
            print(f'Boleto {billing.id} registrado com sucesso')
        
        elif billing_response.status_code == 200 and operation != 'registrar':
            billing.status = status_billing
            billing.save()
            log_santander.message = 'Finalizado com sucesso'
            log_santander.response = billing_response.json()
            log_santander.status = 'success'
            log_santander.save()
            print(f'Boleto {billing.id} atualizado com sucesso')
            
        else:
            status_billing = 'error'
            billing.status = status_billing
            billing.save()
            log_santander.message = f'Code: {billing_response.status_code} - Erro ao integrar boleto'
            log_santander.response = billing_response.json()
            log_santander.status = 'error'
            log_santander.save()
            print(f'Failed to update billing {billing.id}: {billing_response.json()}')
    except Exception as e:
        status_billing = 'error'
        billing.status = status_billing
        billing.save()
        log_santander.message = str(e)
        log_santander.status = 'error'
        log_santander.save()
        print(f'Erro ao atualizar boleto {billing_id}: {str(e)}')