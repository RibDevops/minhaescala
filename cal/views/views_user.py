from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from ..models import Matricula

def home(request):
    return redirect('cal:calendar')

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            return redirect('cal:home')
        messages.error(request, 'Usuário ou senha inválidos')
    return render(request, 'cal/login.html')

def logout_view(request):
    logout(request)
    return redirect('cal:login')

def register_view(request):
    return render(request, 'cal/register.html')

@login_required
def perfil_usuario(request):
    if request.method == 'POST':
        if 'perfil_submit' in request.POST:
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('cal:perfil')
        elif 'password_submit' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('cal:perfil')
    
    password_form = PasswordChangeForm(request.user)
    matricula = getattr(request.user, 'matricula', None)
    return render(request, 'cal/perfil.html', {
        'password_form': password_form,
        'matricula': matricula
    })

def listar_usuarios(request):
    if not request.user.is_staff:
        return redirect('cal:home')
    usuarios = User.objects.all().order_by('username')
    return render(request, 'cal/usuarios_list.html', {'usuarios': usuarios})
