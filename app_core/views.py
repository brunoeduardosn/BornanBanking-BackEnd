from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import Tenant, CustomUser, UserTenant
from .serializers import TenantSerializer, RegisterSerializer
from app_core.decorators import tenant_required
from .forms import LoginForm, TenantSelectForm, TenantForm, CustomUserForm
from django.contrib.auth.decorators import login_required
import uuid

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        usertenants = UserTenant.objects.filter(user=user.id)
        tenants = []
        for tenant in usertenants:
            tenants.append(
            {
                'idTenant': tenant.tenant.id,
                'tenant': tenant.tenant.tenant,
                'is_admin': tenant.is_admin
            })
        
        data.update({
            'user': 
                {    
                'user_id': self.user.id,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name
                },            
            'tenants': tenants
        })

        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ViewsTenants(APIView):
    """
    get:
    Retorna uma lista de todos os tenants ou um tenant específico.

    post:
    Cria um novo tenant.

    put:
    Atualiza um tenant existente.

    delete:
    Deleta um tenant existente.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description']  # Ajuste os campos conforme sua model

    @swagger_auto_schema(
        request_body=TenantSerializer,
        responses={201: TenantSerializer, 400: 'Bad Request'}
    )
    def post(self, request):
        """
        Cria um novo tenant.
        """
        serializer = TenantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Tenant created successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'status': 'error',
                'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        """
        Retorna uma lista de todos os tenants ou um tenant específico.
        """
        if pk:
            try:
                customer = Tenant.objects.get(pk=pk)
            except Tenant.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Customer not found.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = TenantSerializer(customer)
            return Response({
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        queryset = Tenant.objects.all()
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(tenant__icontains=search)

        serializer = TenantSerializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=TenantSerializer,
        responses={200: TenantSerializer, 400: 'Bad Request', 404: 'Not Found'}
    )
    def put(self, request, pk):
        """
        Atualiza um tenant existente.
        """
        try:
            query = Tenant.objects.get(pk=pk)
        except Tenant.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Tenant not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = TenantSerializer(query, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Tenant updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Deleta um tenant existente.
        """
        try:
            query = Tenant.objects.get(pk=pk)
        except Tenant.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Tenant not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        query.delete()
        return Response({
            'status': 'success',
            'message': 'Tenant deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)

class Register(APIView):
    """
    post:
    Registra um novo tenant.
    """
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: 'Success', 400: 'Bad Request'}
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "message": "Novo Tenant registrado com sucesso"}, status=status.HTTP_201_CREATED)
        
        return Response({
                'status': 'error',
                'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirecionar para a página inicial ou outra página
            else:
                form.add_error(None, 'Usuário ou senha inválidos')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirecionar para a página de login

@login_required
def home_view(request):
    tenant_id = request.session.get('tenant_id')
    tenant_name = None
    if tenant_id:
        tenant = Tenant.objects.get(id=uuid.UUID(tenant_id))
        tenant_name = tenant.tenant
    return render(request, 'home.html', {'tenant_name': tenant_name})

def redirect_to_login(request):
    return redirect('/core/login/')

@login_required
def select_tenant(request):
    if request.method == 'POST':
        form = TenantSelectForm(request.POST, user=request.user)
        if form.is_valid():
            tenant = form.cleaned_data['tenant']
            request.session['tenant_id'] = str(tenant.id)  # Converter UUID para string
            return redirect('home')  # Redirecionar para a página inicial ou outra página
    else:
        form = TenantSelectForm(user=request.user)
    return render(request, 'select_tenant.html', {'form': form})

def register(request):
    if request.method == 'POST':
        tenant_form = TenantForm(request.POST)
        user_form = CustomUserForm(request.POST)
        if tenant_form.is_valid() and user_form.is_valid():
            tenant = tenant_form.save()
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            UserTenant.objects.create(user=user, tenant=tenant, is_admin=True)
            login(request, user)
            return redirect('home')  # Redirecionar para a página inicial após o cadastro
    else:
        tenant_form = TenantForm()
        user_form = CustomUserForm()
    return render(request, 'register.html', {'tenant_form': tenant_form, 'user_form': user_form})