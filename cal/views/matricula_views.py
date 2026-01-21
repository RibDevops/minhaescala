# views/matricula_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import Matricula, Hospital, Setor, Especialidade, PerfilUsuario
from ..forms import MatriculaForm

@login_required
def matricula_list(request):
    matriculas = Matricula.objects.all().order_by('nome_guerra')
    
    # Filtros
    search = request.GET.get('search')
    hospital_id = request.GET.get('hospital')
    
    if search:
        matriculas = matriculas.filter(
            Q(matricula__icontains=search) |
            Q(nome_guerra__icontains=search) |
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
        matricula_form = MatriculaForm(request.POST)
        if matricula_form.is_valid():
            matricula = matricula_form.save()
            messages.success(request, f'Matrícula {matricula.matricula} criada com sucesso!')
            return redirect('cal:matricula_list')
    else:
        matricula_form = MatriculaForm()
    
    return render(request, 'cal/matricula/form.html', {
        'matricula_form': matricula_form,
        'title': 'Nova Matrícula',
        'action': 'Criar'
    })

@login_required
def matricula_detail(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    return render(request, 'cal/matricula/detail.html', {
        'matricula': matricula
    })

@login_required
def matricula_update(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    if request.method == 'POST':
        matricula_form = MatriculaForm(request.POST, instance=matricula)
        if matricula_form.is_valid():
            matricula = matricula_form.save()
            messages.success(request, 'Matrícula atualizada com sucesso!')
            return redirect('cal:matricula_detail', pk=matricula.pk)
    else:
        matricula_form = MatriculaForm(instance=matricula)
    
    return render(request, 'cal/matricula/form.html', {
        'matricula_form': matricula_form,
        'title': 'Editar Matrícula',
        'action': 'Atualizar'
    })

@login_required
def matricula_delete(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    if request.method == 'POST':
        matricula.delete()
        messages.success(request, 'Matrícula excluída com sucesso!')
        return redirect('cal:matricula_list')
    return render(request, 'cal/matricula/confirm_delete.html', {
        'matricula': matricula
    })
