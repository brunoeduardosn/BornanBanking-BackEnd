import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now, make_aware
from django.conf import settings
from .models import RequestLog
from datetime import datetime

class RequestLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        
        if request.method in ['POST', 'PUT', 'PATCH']:
            request.body_data = request.body.decode('utf-8') if request.body else ''
        else:
            request.body_data = ''
        request.META.get('HTTP_X_FORWARDED_FOR')

    def process_response(self, request, response):
        execution_time = time.time() - request.start_time  # Calcula o tempo de execução
        request_time = request.start_time  # Armazena o timestamp do início da requisição
        response_time = time.time()  # Captura o timestamp do final da requisição

        # Convertendo os timestamps para datetime e garantindo que eles sejam "timezone-aware"
        request_time_dt = make_aware(datetime.fromtimestamp(request_time))  # Início como datetime
        response_time_dt = make_aware(datetime.fromtimestamp(response_time))  # Fim como datetime


        ip_address = request.META.get('REMOTE_ADDR', '')

        user_agent = request.META.get('HTTP_USER_AGENT', '')

        query_params = request.GET.dict()
        
        tenant_id = request.GET.get('tenant_id') or \
                    (hasattr(request, 'data') and request.data.get('tenant_id')) or \
                    request.headers.get('X-Tenant')
                    
        try:
            post_data = json.loads(request.body_data) if request.method in ['POST', 'PUT', 'PATCH'] and request.body_data else {}
        except json.JSONDecodeError:
            post_data = {}

        user = request.user if request.user.is_authenticated else None

        RequestLog.objects.create(
            user=user,
            path=request.path,
            method=request.method,
            status_code=response.status_code,
            ip_address=ip_address,
            user_agent=user_agent,
            request_time=request_time_dt, 
            response_time=response_time_dt,  
            execution_time=execution_time,  
            query_params=query_params,
            post_data=post_data,
            response_body=self.get_response_body(response)
        )

        if settings.PRINT_LOG:
            self.debug_print_request(request, response, request_time_dt, response_time_dt, execution_time)

        return response

    def get_response_body(self, response):
        """
        Extract and decode response body if it's a JSON or text content.
        """
        if response.get('Content-Type', '').startswith('application/json'):
            try:
                return json.dumps(json.loads(response.content), indent=4)
            except json.JSONDecodeError:
                return response.content.decode('utf-8')
        elif response.get('Content-Type', '').startswith('text/'):
            return response.content.decode('utf-8')
        return ''

    def debug_print_request(self, request, response, request_time_dt, response_time_dt, execution_time):
        """
        Print request and response details for debugging.
        Also save the output in a .log file.
        """
        log_message = f'''
--------------- Novo Request ---------------
User: {request.user}
Method: {request.method}
Path: {request.path}
Request Time: {request_time_dt}
Headers: {dict(request.headers)}
Params: {request.GET.dict()}
Body: {request.body_data if request.method in ['POST', 'PUT', 'PATCH'] else None}
Response Status: {response.status_code}
Response Time: {response_time_dt}
Response: {self.get_response_body(response)}
Execution Time: {execution_time:.2f} seconds
---------------- Finalizado ----------------
        '''
        
        # Grava no console
        print(log_message)
        
        # Grava no arquivo .log
        with open('requests.log', 'a') as f:  # 'a' para adicionar no final do arquivo sem sobrescrever
            f.write(log_message)
