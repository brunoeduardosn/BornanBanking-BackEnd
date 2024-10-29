from django import forms
from .models import Tenant, CustomUser

class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    
class TenantSelectForm(forms.Form):
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['tenant'].queryset = Tenant.objects.filter(usertenant__user=user)

class TenantForm(forms.ModelForm):
    environment = forms.ChoiceField(choices=[('sandbox', 'Sandbox'), ('production', 'Production')], required=True)
    bank = forms.CharField(max_length=20, required=True)

    class Meta:
        model = Tenant
        fields = ['tenant', 'notify_email', 'environment', 'bank']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['environment'].initial = self.instance.preferences.get('environment', '')
            self.fields['bank'].initial = self.instance.preferences.get('bank', '')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.preferences['environment'] = self.cleaned_data['environment']
        instance.preferences['bank'] = self.cleaned_data['bank']
        if commit:
            instance.save()
        return instance


class CustomUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password']