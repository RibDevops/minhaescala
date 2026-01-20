# views/setor_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from ..models import Setor, Hospital
from ..forms import SetorForm

@login_required
def setor_list(request):
    setores = Setor.objects.all().order_by('hospital__nome', 'nome')
    
    # Filtro por hospital
    hospital_id = request.GET.get('hospital')
    if hospital_id:
        setores = setores.filter(hospital_id=hospital_id)
    
    hospitais = Hospital.objects.all()
    
    # Paginação
    paginator = Paginator(setores, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, setor/list.html', {
        'page_obj': page_obj,
        'hospitais': hospitais,
        'selected_hospital': hospital_id,
        'total_count': setores.count()
    })

@login_required
def setor_create(request):
    if request.method == 'POST':
        form = SetorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Setor criado com sucesso!')
            return redirect('setor_list')
    else:
        form = SetorForm()
    
    return render(request, setor/form.html', {
        'form': form,
        'title': 'Novo Setor',
        'action': 'Criar'
    })

@login_required
def setor_update(request, pk):
    setor = get_object_or_404(Setor, pk=pk)
    
    if request.method == 'POST':
        form = SetorForm(request.POST, instance=setor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Setor atualizado com sucesso!')
            return redirect('setor_list')
    else:
        form = SetorForm(instance=setor)
    
    return render(request, setor/form.html', {
        'form': form,
        'title': 'Editar Setor',
        'action': 'Atualizar'
    })

@login_required
def setor_delete(request, pk):
    setor = get_object_or_404(Setor, pk=pk)
    
    if request.method == 'POST':
        setor.delete()
        messages.success(request, 'Setor excluído com sucesso!')
        return redirect('setor_list')
    
    return render(request, setor/confirm_delete.html', {
        'setor': setor
    })