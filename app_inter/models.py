from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid
from app_core.models import Tenant
from app_banks.models import Bank, Billing

class InterConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='app_inter_tenant_configuration')
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='app_inter_bank_configuration')
    client_id = models.CharField(max_length=50)
    client_secret = models.CharField(max_length=50)
    type = models.CharField(max_length=7, default='BILLING')
    workspace = models.CharField(max_length=255, null=True, blank=True)
    webhookURL = models.CharField(max_length=255, null=True, blank=True)
    bankSlipBillingWebhookActive = models.BooleanField(default=False)
    pixBillingWebhookActive = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.tenant.name} - {self.bank.name}'

class InterBilling(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='app_inter_tenant')
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, null=True, blank=True, related_name='app_inter_bank')
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, null=True, blank=True, related_name='app_inter_billing')
    operation = models.CharField(choices=[('REGISTRO', 'REGISTRO'), ('BAIXA', 'BAIXA'), ('ALTERACAO', 'ALTERACAO'), ('CANCELAMENTO', 'CANCELAMENTO')]) # Operação a ser realizada - Nota 5

    # Dados base
    nsu_code = models.CharField(max_length=20) # Número sequencial único por Convênio/Data - Nota 1
    nsu_date = models.DateField() # Data do NSU Gerado - Nota 2
    environment = models.CharField(max_length=10, choices=[('TESTE', 'TESTE'), ('PRODUCAO', 'PRODUCAO')]) # Ambiente para o processamento do registro do boleto - Nota 3
    covenant_code = models.CharField(max_length=9) # Código de identificação do convênio no qual o boleto deverá ser registrado - Nota 4
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
    # Dados do boleto
    bank_number = models.CharField(max_length=13) # Nosso Número - Nota 8
    client_number = models.CharField(max_length=15, null=True, blank=True) # NÃO OBRIGATÓRIO Seu Número - Nota 9
    due_date = models.DateField() # Data de Vencimento
    issue_date = models.DateField() # Data de Emissão
    participant_code = models.CharField(max_length=25) # NÃO OBRIGATÓRIO Controle do Participante - Nota 10
    nominal_value = models.DecimalField(max_digits=15, decimal_places=2) # Valor Nominal
    document_kind = models.CharField(max_length=20) # Espécie do Documento - Nota 11
    # Dados de desconto
    discount_type = models.CharField(max_length=20, null=True, blank=True) # NÃO OBRIGATÓRIO Tipo de Desconto - Nota 12
    discount_one_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # NÃO OBRIGATÓRIO Valor do desconto por antecipação ou primeirodesconto a ser concedido para o boleto 
    discount_one_limit_date = models.DateField(null=True, blank=True) # NÃO OBRIGATÓRIO Data limite do primeiro desconto a ser concedido para o boleto 
    discount_two_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # NÃO OBRIGATÓRIO Valor do segundo desconto a ser concedido para o boleto 
    discount_two_limit_date = models.DateField(null=True, blank=True) # NÃO OBRIGATÓRIO Data limite do segundo desconto a ser concedido para o boleto
    discount_three_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # NÃO OBRIGATÓRIO Valor do terceiro desconto a ser concedido para o boleto
    discount_three_limit_date = models.DateField(null=True, blank=True) # NÃO OBRIGATÓRIO Data limite do terceiro desconto a ser concedido para o boleto
    # Dados de multa e juros
    fine_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # NÃO OBRIGATÓRIO Percentual de multa a ser aplicada para o boleto 
    fine_quantity_days = models.IntegerField(null=True, blank=True) # NÃO OBRIGATÓRIO Quantidade de dias após o vencimento do boleto em que a multa deverá começar a ser aplicada
    interest_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # NÃO OBRIGATÓRIO Percentual de juros ao mês a ser aplicado para o boleto 
    deduction_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # NÃO OBRIGATÓRIO Valor de abatimento a ser concedido para o boleto 
    protest_type = models.CharField(max_length=20, null=True, blank=True) # NÃO OBRIGATÓRIO Tipo de protesto a ser aplicado para o boleto - Nota 13
    protest_quantity_days = models.IntegerField(null=True, blank=True) # NÃO OBRIGATÓRIO Quantidade de dias após o vencimento do boleto em que o protesto deverá ser aplicado - Nota 13
    # Dados de baixa
    writeoff_quantity_days = models.IntegerField(null=True, blank=True) # NÃO OBRIGATÓRIO Quantidade de dias para que um boleto seja baixado após a data de vencimento = Nota 14
    payment_type = models.CharField(max_length=10)  # Tipo de pagamento - Nota 15
    parcels_quantity = models.IntegerField(null=True, blank=True) # NÃO OBRIGATÓRIO Quantidade de parciais a ser atribuída ao boleto em caso de tipo de pagamento “Parcial” - Nota 16
    value_type = models.CharField(max_length=10) # NÃO OBRIGATÓRIO Tipo de valor a ser definido para mínimo e máximo para pagamento, em caso de tipo de pagamento “Divergente” ou “Parcial” - Nota 17
    minvalueorpercentage = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # NÃO OBRIGATÓRIO Valor mínimo ou percentual mínimo a ser definido para pagamento, em caso de tipo de pagamento “Divergente” ou “Parcial” - Nota 18
    maxvalueorpercentage = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # NÃO OBRIGATÓRIO Valor máximo ou percentual máximo a ser definido para pagamento, em caso de tipo de pagamento “Divergente” ou “Parcial” - Nota 19
    iofpercentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # NÃO OBRIGATÓRIO Percentual de IOF a ser aplicado para o boleto - Nota 20
    sharing_code = models.CharField(max_length=2) # NÃO OBRIGATÓRIO Código de partilha cadastrado no convênio do Beneficiário, indica a conta corrente que receberá o crédito - Nota 21
    sharing_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # NÃO OBRIGATÓRIO Valor a ser partilhado para o boleto - Nota 22
    # Dados PIX
    key_type = models.CharField(max_length=10, null=True, blank=True) # NÃO OBRIGATÓRIO Tipo de chave DICT (PIX) a ser vinculada ao boleto - Nota 23
    key_dictkey = models.CharField(max_length=50, null=True, blank=True) # NÃO OBRIGATÓRIO Chave DICT (PIX) a ser vinculada ao boleto - Nota 24
    txid = models.CharField(max_length=50, null=True, blank=True) # NÃO OBRIGATÓRIO Código de Identificação do Qr Code (txId) - Nota 25
    messages = ArrayField(models.CharField(max_length=100), blank=True, default=list) # NÃO OBRIGATÓRIO Mensagens a serem exibidas no boleto - Nota 26
    # Dados Boleto Registrado
    barcode = models.CharField(max_length=44, null=True, blank=True) # Código de Barras do boleto registrado
    digitableline = models.CharField(max_length=47, null=True, blank=True) # Linha Digitável do boleto registrado
    entrydate = models.DateField(null=True, blank=True) # Data de entrada do boleto registrado
    qrcodepix = models.CharField(max_length=255, null=True, blank=True) # QR Code PIX do boleto registrado
    qrcodeurl = models.CharField(max_length=255, null=True, blank=True) # URL do QR Code do boleto registrado

    def __str__(self):
        return f'{self.nsu_code} - {self.bank_number} - {self.client_number} - {self.due_date} - {self.nominal_value}'
    
class InterBillingLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE)
    log = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.billing.nsu_code} - {self.created_at}'
    
class InterBillingPatch(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # Dados de Alteração
    duedate = models.DateField(null=True, blank=True) # Data de Vencimento
    nominalvalue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # Valor Nominal
    operation = models.CharField(choices=[('PROTESTAR', 'PROTESTAR'), ('CANCELAR_PROTESTO ', 'CANCELAR_PROTESTO '), ('BAIXAR', 'BAIXAR')], max_length=20) # Operação a ser realizada no boleto - Nota 31
    protestquantitydays = models.IntegerField(null=True, blank=True) # Alterar Quantidade de Dias de Protesto - Nota 32
    deductionvalue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # Conceder/Cancelar/Alterar Abatimento 
    # Dados de desconto
    discounttype = models.CharField(max_length=20, null=True, blank=True) # Conceder/Cancelar/Alterar Desconto Data fixa - Nota 34
    discount_one_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # Valor do desconto por antecipação ou primeiro desconto a ser concedido para o boleto
    discount_one_limit_date = models.DateField(null=True, blank=True) # Data limite do primeiro desconto a ser concedido para o boleto
    discount_two_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # Valor do segundo desconto a ser concedido para o boleto
    discount_two_limit_date = models.DateField(null=True, blank=True) # Data limite do segundo desconto a ser concedido para o boleto
    discount_three_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # Valor do terceiro desconto a ser concedido para o boleto
    discount_three_limit_date = models.DateField(null=True, blank=True) # Data limite do terceiro desconto a ser concedido para o boleto
    finepercentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # Percentual de multa a ser aplicada para o boleto
    finedate = models.DateField(null=True, blank=True) # Alterar Data de Multa
    interest_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # Percentual de juros ao mês a ser aplicado para o boleto
    interest_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # Valor de juros a ser aplicado para o boleto
    interest_tolerance_date = models.DateField(null=True, blank=True) # Data de Tolerância de Juros
    minvalueorpercentage = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # Valor mínimo ou percentual mínimo a ser definido para pagamento, em caso de tipo de pagamento “Divergente” ou “Parcial”
    maxvalueorpercentage = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) # Valor máximo ou percentual máximo a ser definido para pagamento, em caso de tipo de pagamento “Divergente” ou “Parcial”
    writeoffquantitydays = models.IntegerField(null=True, blank=True) # Quantidade de dias para que um boleto seja baixado após a data de vencimento
    clientnumber = models.CharField(max_length=15, null=True, blank=True) # Seu Número - Nota 9
    participantcode = models.CharField(max_length=25, null=True, blank=True) # Controle do Participante - Nota 10

    def __str__(self):
        return f'{self.billing.nsu_code} - {self.created_at}'