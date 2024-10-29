from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import BankForm
from .models import Bank, Billing
from app_core.models import Tenant
from app_core.decorators import tenant_required, filter_by_tenant
from django.template.loader import render_to_string
from app_santander.tasks import create_workspace as create_workspace_task
from app_santander.models import SantanderConfiguration
import uuid
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Billing
from .serializers import BillingSerializer
from rest_framework import serializers

@login_required
@tenant_required
@filter_by_tenant
def create_bank(request):
    tenant_id = request.session.get('tenant_id')
    if not tenant_id:
        return redirect('select_tenant')  # Redirecionar para selecionar o tenant se não estiver selecionado

    tenant = Tenant.objects.get(id=uuid.UUID(tenant_id))  # Converter string de volta para UUID
    
    if request.method == 'POST':
        form = BankForm(request.POST, tenant_id=tenant_id)
        if form.is_valid():
            bank = form.save(commit=False)
            bank.tenant = tenant
            bank.save()
            return redirect('bank_list')  # Redirecionar para a lista de bancos
    else:
        form = BankForm(initial={'tenant': tenant}, tenant_id=tenant_id)
    return render(request, 'bank_form.html', {'form': form, 'tenant_tenant': tenant.tenant})

@login_required
def home_view(request):
    tenant_id = request.session.get('tenant_id')
    tenant_name = None
    if tenant_id:
        tenant = Tenant.objects.get(id=uuid.UUID(tenant_id))
        tenant_name = tenant.name
    return render(request, 'home.html', {'tenant_name': tenant_name})

@login_required
@tenant_required
@filter_by_tenant
def edit_bank(request, bank_id):
    tenant_id = request.session.get('tenant_id')
    if not tenant_id:
        return redirect('select_tenant')
    
    tenant = Tenant.objects.get(id=uuid.UUID(tenant_id))
    try:
        bank_uuid = uuid.UUID(str(bank_id))  # Converter string para UUID
        request.session['bank_id'] = str(bank_uuid)  # Converter UUID para string
    except ValueError:
        return redirect('bank_list')  # Redirecionar se o UUID for inválido

    bank = get_object_or_404(Bank, id=bank_uuid)
    
    if request.method == 'POST':
        form = BankForm(request.POST, instance=bank, tenant_id=tenant_id)
        if form.is_valid():
            bank = form.save(commit=False)
            bank.tenant = tenant
            bank.save()
            
            configuration = SantanderConfiguration.objects.get(bank=bank, tenant_id=tenant_id)
            if configuration.workspace is None or configuration.workspace == '':
                create_workspace_task(bank.id, configuration.id)
            return redirect('bank_list')
    else:
        form = BankForm(instance=bank, tenant_id=tenant_id)
    
    # Adicionar campos não editáveis ao contexto
    non_editable_fields = {
        'is_created': bank.is_created,
        'is_updated': bank.is_updated,
    }
    
    return render(request, 'bank_form.html', {'form': form, 'tenant_name': tenant.tenant, 'non_editable_fields': non_editable_fields})

@login_required
@tenant_required
@filter_by_tenant
def bank_list(request):
    tenant = request.tenant
    banks = Bank.objects.filter(tenant=tenant)  # Filtrar bancos pelo tenant
    return render(request, 'bank_list.html', {'banks': banks})

@login_required
@tenant_required
@filter_by_tenant
def billing_list(request):
    tenant = request.tenant
    billings = Billing.objects.filter(tenant=tenant)

@api_view(['POST'])
@login_required
def billing_integration(request):
    data_list = request.data
    responses = []

    if not isinstance(data_list, list):
        return Response({'error': 'Invalid data format. Expected a list of dictionaries.'}, status=status.HTTP_400_BAD_REQUEST)

    for data in data_list:
        response_item = {
            "status": None,
            "message": None
        }

        try:
            tenant_id = data.get('tenant')
            bank_id = data.get('bank')
            document = data.get('document')
            status_billing = data.get('status_billing')

            if tenant_id is None or document is None or bank_id is None or status_billing is None:
                raise ValueError("Campos obrigatórios estão faltando")

            tenant = get_object_or_404(Tenant, id=tenant_id)
            bank = get_object_or_404(Bank, id=bank_id)

            # Remover dados para evitar conflito
            data.pop('tenant', None)
            data.pop('bank', None)
            data.pop('status_integration', None)
            data.pop('version', None)

            try:
                billing_instance = Billing.objects.filter(tenant=tenant, document=document, bank=bank).latest('version')
            except Billing.DoesNotExist:
                billing_instance = None
                
            if billing_instance:
                if status_billing == 'canceled':
                    data['status_integration'] = "canceled"
                elif status_billing == 'received':
                    data['status_integration'] = "updated"
                elif status_billing == 'pending':
                    data['status_integration'] = "updated"
                elif status_billing == 'protested':
                    data['status_integration'] = "protested"
                else:
                    data['status_integration'] = "updated"

                version = billing_instance.version
                new_version = version + 1
                data['version'] = new_version
                response_item["message"] = "Boleto atualizado"
            else:
                if status_billing != 'pending':
                    raise ValueError("Não é possível criar um boleto com status diferente de 'pending'")
                data['version'] = 1
                data['status_integration'] = "created"
                response_item["message"] = "Boleto criado"

            data['tenant'] = tenant.id
            data['bank'] = bank.id

            serializer = BillingSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_item["status"] = "success"

        except Tenant.DoesNotExist:
            response_item["status"] = "error"
            response_item["message"] = "Tenant não encontrado"
        except Bank.DoesNotExist:
            response_item["status"] = "error"
            response_item["message"] = "Banco não encontrado"
        except ValueError as ve:
            response_item["status"] = "error"
            response_item["message"] = str(ve)
        except Exception as e:
            response_item["status"] = "error"
            response_item["message"] = str(e)

        responses.append(response_item)

    return Response(responses, status=status.HTTP_200_OK)