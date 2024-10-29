from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('O endereço de email deve ser fornecido'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superusuário deve ter is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superusuário deve ter is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    notify_email = models.EmailField()
    preferences = models.JSONField(default=dict)

    def __str__(self):
        return self.tenant

class UserTenant(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.email} - {self.tenant.tenant}'

    class Meta:
        unique_together = [['user', 'tenant']]

User = get_user_model()

class RequestLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    path = models.CharField(max_length=255)           # URL requisitada
    method = models.CharField(max_length=10)          # Método HTTP (GET, POST, etc.)
    status_code = models.IntegerField()               # Status de resposta (200, 404, etc.)
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # IP do cliente
    user_agent = models.CharField(max_length=255, null=True, blank=True)  # Navegador do cliente
    request_time = models.DateTimeField(default=timezone.now)          # Hora da requisição
    response_time = models.DateTimeField(null=True, blank=True)        # Hora da resposta
    execution_time = models.FloatField(null=True, blank=True)          # Tempo de execução
    query_params = models.TextField(blank=True, null=True)             # Parâmetros de consulta
    post_data = models.TextField(blank=True, null=True)                # Dados de POST
    response_body = models.TextField(blank=True, null=True)            # Corpo da resposta

    def __str__(self):
        return f'{self.method} {self.path} - {self.status_code}'
