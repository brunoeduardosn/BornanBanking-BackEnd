# urls.py
from django.urls import path
from .views import view_teste

urlpatterns = [
    path('test/', view_teste, name='view_teste'),
]