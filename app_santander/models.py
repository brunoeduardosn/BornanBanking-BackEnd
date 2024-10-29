from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid
from app_core.models import Tenant
from app_banks.models import Bank, Billing

class SantanderConfiguration(models.Model):
    DISCOUNT_TYPE = [
        ('ISENTO', 'Isento'),
        ('VALOR_DATA_FIXA', 'Por data fixa'),
        ('VALOR_DIA_CORRIDO', 'Por dia corrido'),
        ('VALOR_DIA_UTIL', 'Por dia útil')
    ]
    
    PROTEST_TYPE = [
        ('SEM_PROTESTO', 'Sem Protesto'),
        ('DIAS_CORRIDOS', 'Dias Corridos'),
        ('DIAS_UTEIS', 'Dias útes'),
        ('CADASTRO_CONVENIO', 'Cadastro do Convênio')
    ]
    
    PAYMENT_TYPE = [
        ('REGISTRO', 'Registro'),
        ('DIVERGENTE', 'Divergente'),
        ('PARCIAL', 'PARCIAL')
    ]
    
    KEY_TYPE = [
        ('CPF', 'CPF'),
        ('CNPJ', 'CNPJ'),
        ('CELULAR', 'CELULAR'),
        ('EMAIL', 'EMAIL'),
        ('EVP', 'EVP')
    ]
    
    # PrimaryKey and ForeignKey
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='app_santander_tenant_configuration')
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='app_santander_bank_configuration')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Dados de Configuração
    client_id = models.CharField(max_length=50)
    client_secret = models.CharField(max_length=50)
    covenant = models.CharField(max_length=9)
    type = models.CharField(max_length=7, default='BILLING')
    workspace = models.CharField(max_length=255, null=True, blank=True)
    webhookURL = models.CharField(max_length=255, null=True, blank=True)
    bankSlipBillingWebhookActive = models.BooleanField(default=False)
    pixBillingWebhookActive = models.BooleanField(default=False)
    
    # Dados Padrões
    messages = ArrayField(models.CharField(max_length=100), blank=True, default=list) # NÃO OBRIGATÓRIO Mensagens a serem exibidas no boleto - Nota 26
    
    # Dados de Juros, Multa e Protesto
    protest_type = models.CharField(choices=PROTEST_TYPE, default='CADASTRO_CONVENIO') # NÃO OBRIGATÓRIO Tipo de protesto
    protest_days = models.IntegerField(null=True, blank=True) # NÃO OBRIGATÓRIO Prazo para protesto
    finepercent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) # NÃO OBRIGATÓRIO Percentual de multa
    finequantitydays = models.IntegerField(null=True, blank=True, default=1) # NÃO OBRIGATÓRIO Quantidade de dias para multa
    interestpercent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) # NÃO OBRIGATÓRIO Percentual de juros
    
    # Dados de Pagamento e Baixa
    payment_type = models.CharField(choices=PAYMENT_TYPE, default='REGISTRO')
    parcels_quantity = models.IntegerField(null=True, blank=True)
    writeoff_quantity_days = models.IntegerField(null=True, blank=True)
    value_type = models.CharField(max_length=10, choices=[('VALOR', 'VALOR'), ('PERCENTUAL', 'PERCENTUAL')], default='VALOR')
    min_value_or_percentage = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    max_value_or_percentage = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Dados de Desconto
    discount_type = models.CharField(choices=DISCOUNT_TYPE)
    discountone_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # NÃO OBRIGATÓRIO Valor do desconto 1
    discountone_limitdate = models.DateField(null=True, blank=True) # NÃO OBRIGATÓRIO Data do desconto 1
    discounttwo_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # NÃO OBRIGATÓRIO Valor do desconto 2
    discounttwo_limitdate = models.DateField(null=True, blank=True) # NÃO OBRIGATÓRIO Data do desconto 2
    discountthree_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # NÃO OBRIGATÓRIO Valor do desconto 3
    discountthree_limitdate = models.DateField(null=True, blank=True) # NÃO OBRIGATÓRIO Data do desconto 3

    # Dados PIX
    key_type = models.CharField(choices=KEY_TYPE, null=True, blank=True) # NÃO OBRIGATÓRIO Tipo de chave PIX
    key_dictkey = models.CharField(max_length=50, null=True, blank=True) # NÃO OBRIGATÓRIO Chave DICT (PIX) a ser vinculada ao boleto - Nota 24
    txid = models.CharField(max_length=50, null=True, blank=True) # NÃO OBRIGATÓRIO Código de Identificação do Qr Code (txId) - Nota 25
    
    class Meta:
        unique_together = ['tenant', 'bank']

    def __str__(self):
        return f'{self.tenant.name} - {self.bank.name}'

class SantanderBillingLog(models.Model):
    TYPE_CHOICES = [
        ('registrar', 'Registrar'),
        ('atualizar', 'Atualizar'),
        ('baixar', 'Baixar'),
        ('protestar', 'Protestar'),
        ('cancelar_protesto', 'Cancelar Protesto'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('success', 'Sucesso'),
        ('error', 'Erro'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    type_integration = models.CharField(max_length=20, choices=TYPE_CHOICES)
    payload = models.TextField(null=True, blank=True) 
    response = models.TextField(null=True, blank=True)  
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.billing.nsu_code} - {self.created_at} - status: {self.status}'
 