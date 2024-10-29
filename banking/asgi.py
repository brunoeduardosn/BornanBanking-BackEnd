import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
#from channels.auth import AuthMiddlewareStack
from banking.middleware import JWTAuthMiddleware
import app_core.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            app_core.routing.websocket_urlpatterns
        )
    ),
})
