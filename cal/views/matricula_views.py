# views/matricula_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import Matricula, Hospital, Setor, Especialidade, PerfilUsuario
from ..forms import MatriculaForm, UserForm, PerfilUsuarioForm

@login_required
def matricula_list(request):
    matriculas = Matricula.objects.all().order_by('nome_exibicao')
    
    # Filtros
    search = request.GET.get('search')
    hospital_id = request.GET.get('hospital')
    especialidade_id = request.GET.get('especialidade')
    
    if search:
        matriculas = matriculas.filter(
            Q(numero__icontains=search) |
            Q(nome_exibicao__icontains=search) |
            Q(nome_completo__icontains=search)
        )
    
    if hospital_id:
        matriculas = matriculas.filter(hospitais__id=hospital_id)
    
    if especialidade_id:
        matriculas = matriculas.filter(especialidades__id=especialidade_id)
    
    hospitais = Hospital.objects.all()
    especialidades = Especialidade.objects.all()
    
    paginator = Paginator(matriculas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, matricula/list.html', {
        'page_obj': page_obj,
        'hospitais': hospitais,
        'especialidades': especialidades,
        'search': search or '',
        'selected_hospital': hospital_id,
        'selected_especialidade': especialidade_id,
        'total_count': matriculas.count()
    })

@login_required
def matricula_create(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        perfil_form = PerfilUsuarioForm(request.POST)
        matricula_form = MatriculaForm(request.POST)
        
        if user_form.is_valid() and perfil_form.is_valid() and matricula_form.is_valid():
            # 1. Criar User
            user = user_form.save(commit=False)
            # Define uma senha padrão baseada na matrícula ou fixa
            matricula_numero = matricula_form.cleaned_data.get('numero')
            user.set_password(matricula_numero or 'senha123')
            user.save()
            
            # 2. Criar PerfilUsuario
            perfil = perfil_form.save(commit=False)
            perfil.user = user
            # Garante que o tipo seja PROFISSIONAL se não especificado
            if not perfil.tipo_usuario:
                perfil.tipo_usuario = 'PROFISSIONAL'
            perfil.save()
            
            # 3. Criar Matricula
            matricula = matricula_form.save(commit=False)
            matricula.perfil = perfil
            matricula.save()
            matricula_form.save_m2m()  # Salvar relações ManyToMany
            
            messages.success(request, f'Matrícula e usuário ({user.username}) criados com sucesso! Senha inicial: {matricula_numero or "senha123"}')
            return redirect('cal:matricula_list')
    else:
        user_form = UserForm()
        perfil_form = PerfilUsuarioForm(initial={'tipo_usuario': 'PROFISSIONAL'})
        matricula_form = MatriculaForm()
    
    return render(request, 'cal/matricula/form.html', {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'matricula_form': matricula_form,
        'title': 'Nova Matrícula',
        'action': 'Criar'
    })

@login_required
def matricula_detail(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    
    return render(request, matricula/detail.html', {
        'matricula': matricula
    })

@login_required
def matricula_update(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    user = matricula.perfil.user
    perfil = matricula.perfil
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        perfil_form = PerfilUsuarioForm(request.POST, instance=perfil)
        matricula_form = MatriculaForm(request.POST, instance=matricula)
        
        if all([user_form.is_valid(), perfil_form.is_valid(), matricula_form.is_valid()]):
            user_form.save()
            perfil_form.save()
            matricula = matricula_form.save()
            matricula_form.save_m2m()
            
            messages.success(request, 'Matrícula atualizada com sucesso!')
            return redirect('matricula_detail', pk=matricula.pk)
    else:
        user_form = UserForm(instance=user)
        perfil_form = PerfilUsuarioForm(instance=perfil)
        matricula_form = MatriculaForm(instance=matricula)
    
    return render(request, matricula/form.html', {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'matricula_form': matricula_form,
        'title': 'Editar Matrícula',
        'action': 'Atualizar'
    })

@login_required
def matricula_delete(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    
    if request.method == 'POST':
        # Deletar em cascata: Matricula -> PerfilUsuario -> User
        matricula.delete()
        messages.success(request, 'Matrícula excluída com sucesso!')
        return redirect('matricula_list')
    
    return render(request, matricula/confirm_delete.html', {
        'matricula': matricula
    })