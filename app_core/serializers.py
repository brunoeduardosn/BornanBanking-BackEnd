from rest_framework import serializers
from .models import CustomUser, Tenant, UserTenant

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    tenant = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password', 'tenant']

    def create(self, validated_data):
        tenant_name = validated_data.pop('tenant')
        password = validated_data.pop('password')

        # Cria o usuário
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Cria o tenant
        tenant = Tenant.objects.create(tenant=tenant_name)

        # Cria a relação entre o usuário e o tenant na tabela UserTenant
        UserTenant.objects.create(user=user, tenant=tenant, is_admin=True)

        return user
