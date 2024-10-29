# views.py
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app_santander.tasks import create_workspace, billing_register

@csrf_exempt
def view_teste(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            tenant_id = data.get('tenant_id')
            bank_id = data.get('bank_id')
            configuration_id = data.get('configuration_id')
            billing_id = data.get('billing_id')
            operation = data.get('operation')
            print(f'Data: {data}')
            print(f'Tenant ID: {tenant_id}')
            print(f'Bank ID: {bank_id}')
            print(f'Configuration ID: {configuration_id}')
            print(f'Billing ID: {billing_id}')
            print(f'Operation: {operation}')
            if not bank_id:
                return JsonResponse({'error': 'bank_id is required'}, status=400)
            
            # Chamar a função create_workspace com o bank_id
            #create_workspace(tenant_id, bank_id, configuration_id)
            billing_register(tenant_id, bank_id, billing_id, operation)
            
            return JsonResponse({'message': 'Finalizado com sucesso'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)