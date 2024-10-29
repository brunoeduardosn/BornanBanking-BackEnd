from django.urls import path
from app_core.views import CustomTokenObtainPairView  # Import da nova view
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ViewsTenants, Register, login_view, home_view, logout_view, select_tenant, register

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', home_view, name='home'), 
    path('select_tenant/', select_tenant, name='select_tenant'),  # Selecionar tenant
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', Register.as_view(), name='register'),
    path('api/tenants/', ViewsTenants.as_view(), name='ViewsTenants'),
    path('api/tenants/<uuid:pk>/', ViewsTenants.as_view(), name='ViewsTenants'),
]
