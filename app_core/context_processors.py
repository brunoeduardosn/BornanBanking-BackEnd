from .models import Tenant
import uuid

def tenant_context(request):
    tenant_name = None
    tenant_id = request.session.get('tenant_id')
    if tenant_id:
        try:
            tenant = Tenant.objects.get(id=uuid.UUID(tenant_id))
            tenant_name = tenant.tenant
        except Tenant.DoesNotExist:
            pass
    return {'tenant_name': tenant_name}