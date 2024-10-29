from django import forms
from django.forms import inlineformset_factory
from .models import Configuration

class CovenantForm(forms.ModelForm):
    class Meta:
        model = Configuration
        fields = ['description', 'client_id', 'client_secret', 'type', 'workspace', 'webhookURL', 'bankSlipBillingWebhookActive', 'pixBillingWebhookActive', 'is_active']

    def __init__(self, *args, **kwargs):
        self.tenant_id = kwargs.pop('tenant_id', None)
        self.bank_id = kwargs.pop('bank_id', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.tenant_id = self.tenant_id  # Usar tenant_id da sessão
        instance.bank_id = self.bank_id # Usar bank_id da sessão
        if commit:
            instance.save()
        return instance