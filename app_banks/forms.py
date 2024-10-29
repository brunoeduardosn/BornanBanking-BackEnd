# forms.py
from django import forms
from .models import Bank
from app_santander.models import SantanderConfiguration
from app_inter.models import InterConfiguration

BANK_CODES = [
    ('033', 'Banco Santander'),
    ('077', 'Banco Inter'),
    # Adicione outros códigos de banco conforme necessário
]

class BankForm(forms.ModelForm):
    bank_code = forms.ChoiceField(choices=BANK_CODES)
    environment = forms.ChoiceField(choices=[('sandbox', 'Sandbox'), ('production', 'Produção')], required=False)

    class Meta:
        model = Bank
        fields = ['name', 'bank_code', 'active', 'environment']
        labels = {
            'name': 'Nome do Banco',
            'bank_code': 'Código do Banco',
            'active': 'Ativo',
            'environment': 'Ambiente',
        }

    def __init__(self, *args, **kwargs):
        self.tenant_id = kwargs.pop('tenant_id', None)
        super().__init__(*args, **kwargs)
        
        # Adicionar campos dinamicamente com base no bank_code
        bank_code = self.initial.get('bank_code') or self.instance.bank_code
        if bank_code == '077':
            self.fields['agencia'] = forms.CharField(max_length=20, label='Agência')
            self.fields['conta_corrente'] = forms.CharField(max_length=20, label='Conta Corrente')
            # Carregar dados do modelo InterConfiguration
            try:
                config = InterConfiguration.objects.get(bank=self.instance, tenant_id=self.tenant_id)
                self.fields['agencia'].initial = config.agencia
                self.fields['conta_corrente'].initial = config.conta_corrente
            except InterConfiguration.DoesNotExist:
                pass
        elif bank_code == '033':
            self.fields['client_id'] = forms.CharField(max_length=50, required=True, label='Client ID')
            self.fields['client_secret'] = forms.CharField(max_length=50, required=True, label='Cliente Secret')
            self.fields['covenant'] = forms.CharField(max_length=9, required=True, label='Convênio')
            self.fields['type'] = forms.CharField(max_length=7, initial='BILLING', label='Tipo')
            self.fields['workspace'] = forms.CharField(max_length=255, required=False, label='Espaço de Trabalho')
            self.fields['webhookURL'] = forms.CharField(max_length=255, required=False, label='URL do Webhook')
            self.fields['bankSlipBillingWebhookActive'] = forms.BooleanField(required=False, label='Webhook de Boleto Ativo')
            self.fields['pixBillingWebhookActive'] = forms.BooleanField(required=False, label='Webhook de PIX Ativo')
            #self.fields['messages'] = forms.CharField(required=False, label='Mensagens')
            self.fields['protest_type'] = forms.ChoiceField(choices=SantanderConfiguration.PROTEST_TYPE, initial='CADASTRO_CONVENIO', label='Tipo de Protesto')
            self.fields['protest_days'] = forms.IntegerField(required=False, label='Prazo para Protesto')
            self.fields['finepercent'] = forms.DecimalField(max_digits=5, decimal_places=2, initial=0.00, label='Percentual de Multa')
            self.fields['finequantitydays'] = forms.IntegerField(initial=1, label='Quantidade de Dias para Multa')
            self.fields['interestpercent'] = forms.DecimalField(max_digits=5, decimal_places=2, initial=0.00, label='Percentual de Juros')
            self.fields['payment_type'] = forms.ChoiceField(choices=SantanderConfiguration.PAYMENT_TYPE, initial='REGISTRO', label='Tipo de Pagamento')
            self.fields['parcels_quantity'] = forms.IntegerField(required=False, label='Quantidade de Parcelas')
            self.fields['writeoff_quantity_days'] = forms.IntegerField(required=False, label='Quantidade de Dias para Baixa')
            self.fields['value_type'] = forms.ChoiceField(choices=[('VALOR', 'VALOR'), ('PERCENTUAL', 'PERCENTUAL')], initial='VALOR', label='Tipo de Valor')
            self.fields['min_value_or_percentage'] = forms.DecimalField(max_digits=15, decimal_places=2, required=False, label='Valor Mínimo ou Percentual')
            self.fields['max_value_or_percentage'] = forms.DecimalField(max_digits=15, decimal_places=2, required=False, label='Valor Máximo ou Percentual')
            self.fields['discount_type'] = forms.ChoiceField(choices=SantanderConfiguration.DISCOUNT_TYPE, label='Tipo de Desconto')
            self.fields['discountone_value'] = forms.DecimalField(max_digits=15, decimal_places=2, required=False, label='Valor do Desconto 1')
            self.fields['discountone_limitdate'] = forms.DateField(required=False, label='Data do Desconto 1')
            self.fields['discounttwo_value'] = forms.DecimalField(max_digits=15, decimal_places=2, required=False, label='Valor do Desconto 2')
            self.fields['discounttwo_limitdate'] = forms.DateField(required=False, label='Data do Desconto 2')
            self.fields['discountthree_value'] = forms.DecimalField(max_digits=15, decimal_places=2, required=False, label='Valor do Desconto 3')
            self.fields['discountthree_limitdate'] = forms.DateField(required=False, label='Data do Desconto 3')
            self.fields['key_type'] = forms.ChoiceField(choices=SantanderConfiguration.KEY_TYPE, label='Tipo de Chave')
            self.fields['key_dictkey'] = forms.CharField(max_length=50, required=False, label='Chave DICT')
            self.fields['txid'] = forms.CharField(max_length=50, required=False, label='Código de Identificação do Qr Code')
            
            try:
                config = SantanderConfiguration.objects.get(bank=self.instance, tenant_id=self.tenant_id)
                self.fields['client_id'].initial = config.client_id
                self.fields['client_secret'].initial = config.client_secret
                self.fields['type'].initial = config.type
                self.fields['workspace'].initial = config.workspace
                self.fields['webhookURL'].initial = config.webhookURL
                self.fields['bankSlipBillingWebhookActive'].initial = config.bankSlipBillingWebhookActive
                self.fields['pixBillingWebhookActive'].initial = config.pixBillingWebhookActive
                #self.fields['messages'].initial = config.messages
                self.fields['protest_type'].initial = config.protest_type
                self.fields['protest_days'].initial = config.protest_days
                self.fields['finepercent'].initial = config.finepercent
                self.fields['finequantitydays'].initial = config.finequantitydays
                self.fields['interestpercent'].initial = config.interestpercent
                self.fields['payment_type'].initial = config.payment_type
                self.fields['parcels_quantity'].initial = config.parcels_quantity
                self.fields['writeoff_quantity_days'].initial = config.writeoff_quantity_days
                self.fields['value_type'].initial = config.value_type
                self.fields['min_value_or_percentage'].initial = config.min_value_or_percentage
                self.fields['max_value_or_percentage'].initial = config.max_value_or_percentage
                self.fields['discount_type'].initial = config.discount_type
                self.fields['discountone_value'].initial = config.discountone_value
                self.fields['discountone_limitdate'].initial = config.discountone_limitdate
                self.fields['discounttwo_value'].initial = config.discounttwo_value
                self.fields['discounttwo_limitdate'].initial = config.discounttwo_limitdate
                self.fields['discountthree_value'].initial = config.discountthree_value
                self.fields['discountthree_limitdate'].initial = config.discountthree_limitdate
                self.fields['key_type'].initial = config.key_type
                self.fields['key_dictkey'].initial = config.key_dictkey
                self.fields['txid'].initial = config.txid
            except SantanderConfiguration.DoesNotExist:
                pass

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.tenant_id = self.tenant_id  # Usar tenant_id da sessão
        
        # Salvar campos adicionais no modelo Configuration
        bank_code = self.cleaned_data.get('bank_code')
        if bank_code == '077':
            config, created = InterConfiguration.objects.get_or_create(bank=instance, tenant_id=self.tenant_id)
            config.agencia = self.cleaned_data.get('agencia', '')
            config.conta_corrente = self.cleaned_data.get('conta_corrente', '')
            config.save()
        elif bank_code == '033':
            config, created = SantanderConfiguration.objects.get_or_create(bank=instance, tenant_id=self.tenant_id)
            config.client_id = self.cleaned_data.get('client_id', '')
            config.client_secret = self.cleaned_data.get('client_secret', '')
            config.type = self.cleaned_data.get('type', 'BILLING')
            config.workspace = self.cleaned_data.get('workspace', '')
            config.webhookURL = self.cleaned_data.get('webhookURL', '')
            config.bankSlipBillingWebhookActive = self.cleaned_data.get('bankSlipBillingWebhookActive', False)
            config.pixBillingWebhookActive = self.cleaned_data.get('pixBillingWebhookActive', False)
            #config.messages = self.cleaned_data.get('messages', '')
            config.protest_type = self.cleaned_data.get('protest_type', 'CADASTRO_CONVENIO')
            config.protest_days = self.cleaned_data.get('protest_days', None)
            config.finepercent = self.cleaned_data.get('finepercent', 0.00)
            config.finequantitydays = self.cleaned_data.get('finequantitydays', 1)
            config.interestpercent = self.cleaned_data.get('interestpercent', 0.00)
            config.payment_type = self.cleaned_data.get('payment_type', 'REGISTRO')
            config.parcels_quantity = self.cleaned_data.get('parcels_quantity', None)
            config.writeoff_quantity_days = self.cleaned_data.get('writeoff_quantity_days', None)
            config.value_type = self.cleaned_data.get('value_type', 'VALOR')
            config.min_value_or_percentage = self.cleaned_data.get('min_value_or_percentage', None)
            config.max_value_or_percentage = self.cleaned_data.get('max_value_or_percentage', None)
            config.discount_type = self.cleaned_data.get('discount_type', 'NAO_CONCEDER_DESCONTO')
            config.discountone_value = self.cleaned_data.get('discountone_value', None)
            config.discountone_limitdate = self.cleaned_data.get('discountone_limitdate', None)
            config.discounttwo_value = self.cleaned_data.get('discounttwo_value', None)
            config.discounttwo_limitdate = self.cleaned_data.get('discounttwo_limitdate', None)
            config.discountthree_value = self.cleaned_data.get('discountthree_value', None)
            config.discountthree_limitdate = self.cleaned_data.get('discountthree_limitdate', None)
            config.key_type = self.cleaned_data.get('key_type', None)
            config.key_dictkey = self.cleaned_data.get('key_dictkey', None)
            config.txid = self.cleaned_data.get('txid', None)
            config.save()
        
        if commit:
            instance.save()
        return instance