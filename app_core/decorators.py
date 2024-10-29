from functools import wraps
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Tenant, UserTenant

def tenant_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        tenant_id = request.session.get('tenant_id')
        if not tenant_id:
            return JsonResponse({'status': 'error', 'message': 'Tenant not selected.'}, status=400)

        tenant = get_object_or_404(Tenant, id=tenant_id)

        # Verifica se o usuário tem permissão para acessar o tenant
        if not UserTenant.objects.filter(user=request.user, tenant=tenant).exists():
            return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)

        # Adiciona o tenant ao request para ser usado na view
        request.tenant = tenant

        # Chama a view original
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def filter_by_tenant(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        tenant = request.tenant
        response = view_func(request, *args, **kwargs)
        
        if isinstance(response, JsonResponse):
            return response

        # Filtra os dados no contexto do template
        if isinstance(response, dict):
            for key, value in response.items():
                if hasattr(value, 'filter'):
                    response[key] = value.filter(tenant=tenant)
        elif hasattr(response, 'context_data'):
            for key, value in response.context_data.items():
                if hasattr(value, 'filter'):
                    response.context_data[key] = value.filter(tenant=tenant)
        return response
    
    return _wrapped_view