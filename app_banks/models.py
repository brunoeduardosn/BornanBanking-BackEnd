from django.db import models
from app_core.models import Tenant
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
import uuid

class Bank(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=3)
    environment = models.CharField(max_length=10, choices=[('sandbox', 'Sandbox'), ('production', 'Produção')])
    active = models.BooleanField(default=True)
    is_created = models.DateField(auto_now_add=True)
    is_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.name} - {self.bank_code} - ID: {self.id}'
    
class Billing(models.Model):
    STATUS_INTEGRATION = [
        ('created', 'Criado'),
        ('updated', 'Atualizado'),
        ('registered', 'Registrado'),
        ('canceled', 'Cancelado'),
        ('received', 'Recebido'),
        ('protest', 'Protestado'),
        ('cancel_protest', 'Cancelado Protesto'),
        ('processing', 'Processando'),
        ('error', 'Erro')
    ]
    
    STATUS_BILLING = [
        ('pending', 'Pendente'),
        ('received', 'Recebido'),
        ('canceled', 'Cancelado'),
        ('protested', 'Protestado'),
        ('error', 'Erro')
    ]
    
    DOCUMENT_KIND = [
        ('DUPLICATA_MERCANTIL', 'Duplicata Mercantil'),
        ('DUPLICATA_SERVICO', 'Duplicata de Serviço'),
        ('NOTA_PROMISSORIA', 'Nota Promissória'),
        ('NOTA_PROMISSORIA_RURAL', 'Nota Promissória Rural'),
        ('RECIBO', 'Recibo'),
        ('APOLICE_SEGURO', 'Apólice de Seguro'),
        ('BOLETO_CARTAO_CREDITO', 'Boleto de Cartão de Crédito'),
        ('BOLETO_PROPOSTA', 'Boleto de Proposta'),
        ('BOLETO_DEPOSITO_APORTE', 'Boleto Depósito Aporte'),
        ('CHEQUE', 'Cheque'),
        ('NOTA_PROMISSORIA_DIRETA', 'Nota Promissória Direta'),
        ('OUTROS', 'Outros')
    ]
    
    PROTEST_TYPE = [
        ('SEM_PROTESTO', 'Sem Protesto'),
        ('DIAS_CORRIDOS', 'Dias Corridos'),
        ('DIAS_UTEIS', 'Dias útes'),
        ('CADASTRO_CONVENIO', 'Cadastro do Convênio')
    ]
    
    # PrimaryKey and ForeignKey
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    
    # Dados do boleto
    status_billing = models.CharField(max_length=20, choices=STATUS_BILLING, default='pending') # Status do pagamento do boleto
    status_integration = models.CharField(max_length=20, choices=STATUS_INTEGRATION, default='created') # Status do boleto
    document = models.CharField(max_length=20) # Número único do documento
    bank_number = models.CharField(max_length=20) # Nosso Número - Nota 8
    issue_date = models.DateField() # Data de Emissão
    document_kind = models.CharField(choices=DOCUMENT_KIND)
    version = models.IntegerField(default=1) # Versão do boleto
    
    # Dados de Valores e Vencimento
    due_date = models.DateField() # Data de Vencimento
    nominal_value = models.DecimalField(max_digits=15, decimal_places=2) # Valor Nominal
    deduction_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00) # NÃO OBRIGATÓRIO Valor de desconto
    fine_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00) # NÃO OBRIGATÓRIO Valor de multa
    interest_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00) # NÃO OBRIGATÓRIO Valor de juros
    protest_type = models.CharField(choices=PROTEST_TYPE, default='CADASTRO_CONVENIO') # NÃO OBRIGATÓRIO Tipo de protesto
    
    # Dados do pagador
    payer_document_type = models.CharField(max_length=4, choices=[('CPF', 'CPF'), ('CNPJ', 'CNPJ')]) # Tipo do documento do pagador original do boleto 
    payer_document_number = models.CharField(max_length=15) # Número do documento do pagador original do boleto - Nota 6
    payer_name = models.CharField(max_length=40) # Nome completo ou razão social do pagador original do boleto 
    payer_address = models.CharField(max_length=40) # Endereço do pagador original do boleto
    payer_neighborhood = models.CharField(max_length=30) # Bairro do pagador original do boleto
    payer_city = models.CharField(max_length=20) # Cidade do pagador original do boleto
    payer_state = models.CharField(max_length=2) # Estado do pagador original do boleto
    payer_zip_code = models.CharField(max_length=9) # CEP do pagador original do boleto (Incluir "-" 00000-000)
    
    # Dados do beneficiário
    beneficiary_document_type = models.CharField(max_length=4, choices=[('CPF', 'CPF'), ('CNPJ', 'CNPJ')], null=True, blank=True) # NÃO OBRIGATÓRIO Tipo do documento do beneficiário
    beneficiary_document_number = models.CharField(max_length=15, null=True, blank=True) # NÃO OBRIGATÓRIO Número do documento do beneficiário
    beneficiary_name = models.CharField(max_length=40, null=True, blank=True) # NÃO OBRIGATÓRIO Nome completo ou razão social do beneficiário
    
    # Dados Boleto Registrado
    barcode = models.CharField(max_length=44, null=True, blank=True) # Código de Barras do boleto registrado
    digitableline = models.CharField(max_length=47, null=True, blank=True) # Linha Digitável do boleto registrado
    entrydate = models.DateField(null=True, blank=True) # Data de entrada do boleto registrado
    qrcodepix = models.CharField(max_length=255, null=True, blank=True) # QR Code PIX do boleto registrado
    qrcodeurl = models.CharField(max_length=255, null=True, blank=True) # URL do QR Code do boleto registrado
    
    class Meta:
        unique_together = ['tenant', 'document', 'bank_number', 'version']

    def __str__(self):
        return f'{self.document} - {self.bank_number}'
    