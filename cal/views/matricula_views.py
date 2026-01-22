from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from ..models import Matricula, PerfilUsuario
from ..forms import MatriculaSimplificadaForm

@login_required
def matricula_list(request):
    matriculas = Matricula.objects.all().select_related('user', 'perfil', 'hospital', 'setor')
    return render(request, 'cal/matricula/list.html', {'matriculas': matriculas})

@login_required
def matricula_create(request):
    if request.method == 'POST':
        form = MatriculaSimplificadaForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Criar Usuário
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password']
                    )
                    
                    # 2. Criar Perfil
                    perfil = PerfilUsuario.objects.create(
                        user=user,
                        tipo=form.cleaned_data['tipo_perfil']
                    )
                    
                    # 3. Criar Matrícula vinculada
                    matricula = form.save(commit=False)
                    matricula.user = user
                    matricula.perfil = perfil
                    matricula.save()
                    
                messages.success(request, f"Matrícula, usuário e perfil de {matricula.nome_guerra} criados com sucesso!")
                return redirect('cal:matricula_list')
            except Exception as e:
                messages.error(request, f"Erro ao criar registro: {str(e)}")
    else:
        form = MatriculaSimplificadaForm()
    
    return render(request, 'cal/matricula/form.html', {'form': form, 'title': 'Nova Matrícula Simplificada'})

@login_required
def matricula_update(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    if request.method == 'POST':
        form = MatriculaSimplificadaForm(request.POST, instance=matricula)
        # Ajustes para edição
        if 'username' in form.fields:
            form.fields['username'].required = False
            form.fields['password'].required = False
            
        if form.is_valid():
            form.save()
            if matricula.perfil:
                matricula.perfil.tipo = form.cleaned_data['tipo_perfil']
                matricula.perfil.save()
            
            messages.success(request, "Dados atualizados com sucesso.")
            return redirect('cal:matricula_list')
    else:
        initial = {}
        if matricula.user:
            initial['username'] = matricula.user.username
            initial['email'] = matricula.user.email
        if matricula.perfil:
            initial['tipo_perfil'] = matricula.perfil.tipo
        form = MatriculaSimplificadaForm(instance=matricula, initial=initial)
        form.fields['username'].disabled = True
        form.fields['password'].required = False
    
    return render(request, 'cal/matricula/form.html', {'form': form, 'title': 'Editar Matrícula'})

@login_required
def matricula_detail(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    return render(request, 'cal/matricula/detail.html', {'matricula': matricula})

@login_required
def matricula_delete(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    if request.method == 'POST':
        user = matricula.user
        matricula.delete()
        if user:
            user.delete()
        messages.success(request, "Matrícula e usuário removidos com sucesso.")
        return redirect('cal:matricula_list')
    return render(request, 'cal/matricula/confirm_delete.html', {'matricula': matricula})
