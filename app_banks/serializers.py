# serializers.py
from rest_framework import serializers
from .models import Billing

class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = '__all__'

'''
    def validate(self, data):
        if self.instance and self.instance.status_billing != 'canceled':
            # Lista de campos que não podem ser alterados
            print('Chamou validacao')
            immutable_fields = [
                'document', 'nominal_value', 'payer_document_type', 
                'payer_document_number', 'payer_name', 'payer_address', 
                'payer_neighborhood', 'payer_city', 'payer_state', 'payer_zip_code', 
                'beneficiary_document_type', 'beneficiary_document_number', 'beneficiary_name'
            ]
            for field in immutable_fields:
                if field in data and data[field] != getattr(self.instance, field):
                    raise serializers.ValidationError({field: f'O campo {field} não pode ser alterado.'})
        return data
'''