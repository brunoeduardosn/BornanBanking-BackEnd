from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Tenant, UserTenant

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['email']
    ordering = ['email']
    
    
@admin.register(Tenant)
class Tenant(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'created_at')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserTenant)