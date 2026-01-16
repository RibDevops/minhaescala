# cal/views/views_login.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, login as login_django
from django.contrib import messages
from cal.forms import UserRegisterForm
from django.urls import reverse_lazy
import logging

logger = logging.getLogger('django')

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Criar perfil padrão
            from cal.models import PerfilUsuario
            PerfilUsuario.objects.get_or_create(user=user)
            
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso!')
            logger.info(f'Novo usuário registrado: {user.username}')
            return redirect('cal:home')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('cal:home')
        return render(request, 'registration/login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            login_django(request, user)
            return redirect('cal:home')
        else:
            messages.error(request, 'Usuário ou senha inválidos. Por favor, tente novamente.')
            return render(request, 'registration/login.html')

from django.contrib.auth.views import LogoutView

def logout_view(request):
    logout(request)
    return redirect('cal:login')
