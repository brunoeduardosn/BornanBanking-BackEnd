# banks/urls.py
from django.urls import path
from .views import bank_list, create_bank, edit_bank, billing_integration

urlpatterns = [
    path('bank/', bank_list, name='bank_list'),  # URL para a lista de bancos
    path('bank/create/', create_bank, name='create_bank'),
    path('bank/edit/<uuid:bank_id>/', edit_bank, name='edit_bank'),  # Editar banco
    path('billing/create/', billing_integration, name='billing_integration'),  
]