from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.schemas import get_schema_view
from rest_framework import permissions
from rest_framework.documentation import include_docs_urls
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from app_core.views import redirect_to_login


schema_view = get_schema_view(
    openapi.Info(
        title="Bornan Soluções API",
        default_version='v1',
        description="Conjunto de API's para o sistema Bancário Bornan",
        terms_of_service="https://www.bornan.com.br/policies/terms/",
        contact=openapi.Contact(email="contato@bornan.com.br"),
        license=openapi.License(name="Bornan License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(JWTAuthentication,)
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('core/', include('app_core.urls')),
    path('banks/', include('app_banks.urls')),
    path('santander/', include('app_santander.urls')),
    path('', redirect_to_login),  # Redirecionar a URL raiz para a página de login
    ]
