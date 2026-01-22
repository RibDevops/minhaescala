from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import Matricula, PerfilUsuario, Hospital
from ..forms import MatriculaSimplificadaForm

@login_required
def matricula_list(request):
    matriculas = Matricula.objects.all().select_related('user', 'perfil', 'hospital', 'setor').order_by('nome_exibicao')
    
    # Filtros
    search = request.GET.get('search')
    hospital_id = request.GET.get('hospital')
    
    if search:
        matriculas = matriculas.filter(
            Q(matricula__icontains=search) |
            Q(nome_exibicao__icontains=search) |
            Q(nome_completo__icontains=search)
        )
    
    if hospital_id:
        matriculas = matriculas.filter(hospital_id=hospital_id)
    
    hospitais = Hospital.objects.all()
    
    paginator = Paginator(matriculas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'cal/matricula/list.html', {
        'page_obj': page_obj,
        'hospitais': hospitais,
        'search': search or '',
        'selected_hospital': hospital_id,
        'total_count': matriculas.count()
    })

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
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name']
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
                    # Gera o nome completo a partir dos campos de nome
                    matricula.nome_completo = f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}".strip()
                    matricula.save()
                    
                messages.success(request, f"Matrícula, usuário e perfil de {matricula.nome_exibicao} criados com sucesso!")
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
            if matricula.user:
                matricula.user.first_name = form.cleaned_data['first_name']
                matricula.user.last_name = form.cleaned_data['last_name']
                matricula.user.email = form.cleaned_data['email']
                matricula.user.save()

            # Atualiza o nome completo da matrícula
            matricula.nome_completo = f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}".strip()
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
            initial['first_name'] = matricula.user.first_name
            initial['last_name'] = matricula.user.last_name
        if matricula.perfil:
            initial['tipo_perfil'] = matricula.perfil.tipo
        form = MatriculaSimplificadaForm(instance=matricula, initial=initial)
        form.fields['username'].disabled = True
        form.fields['password'].required = False
    
    return render(request, 'cal/matricula/form.html', {'form': form, 'title': 'Editar Matrícula'})

@login_required
def matricula_toggle_status(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    if request.method == 'POST':
        matricula.ativo = not matricula.ativo
        matricula.save()
        status = "ativada" if matricula.ativo else "desativada"
        messages.success(request, f"Matrícula de {matricula.nome_exibicao} {status} com sucesso.")
    return redirect('cal:matricula_list')

@login_required
def matricula_detail(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    return render(request, 'cal/matricula/detail.html', {'matricula': matricula})

@login_required
def matricula_delete(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    if request.method == 'POST':
        user = matricula.user
        # Se houver um perfilUsuario no app 'accounts', ele pode estar causando o erro no cascade.
        # Mas o erro diz 'no such table: accounts_perfilusuario', o que indica que algo
        # está tentando acessar uma tabela que não foi criada ou migrada.
        try:
            with transaction.atomic():
                if user:
                    # Deletar o usuário deletará o perfil e a matrícula via CASCADE
                    # Mas vamos deletar a matrícula primeiro para ser explícito
                    matricula.delete()
                    user.delete()
                else:
                    matricula.delete()
            messages.success(request, "Matrícula e usuário removidos com sucesso.")
        except Exception as e:
            messages.error(request, f"Erro ao excluir: {str(e)}")
        return redirect('cal:matricula_list')
    return render(request, 'cal/matricula/confirm_delete.html', {'matricula': matricula})
