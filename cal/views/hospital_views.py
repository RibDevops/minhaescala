# views/hospital_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from ..models import Hospital
from ..forms import HospitalForm

@login_required
def hospital_list(request):
    hospitais = Hospital.objects.all().order_by('nome')
    
    # Paginação
    paginator = Paginator(hospitais, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, hospital/list.html', {
        'page_obj': page_obj,
        'total_count': hospitais.count()
    })

@login_required
def hospital_create(request):
    if request.method == 'POST':
        form = HospitalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hospital criado com sucesso!')
            return redirect('hospital_list')
    else:
        form = HospitalForm()
    
    return render(request, hospital/form.html', {
        'form': form,
        'title': 'Novo Hospital',
        'action': 'Criar'
    })

@login_required
def hospital_detail(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    setores = hospital.setores.all()
    
    return render(request, hospital/detail.html', {
        'hospital': hospital,
        'setores': setores
    })

@login_required
def hospital_update(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    
    if request.method == 'POST':
        form = HospitalForm(request.POST, instance=hospital)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hospital atualizado com sucesso!')
            return redirect('hospital_detail', pk=hospital.pk)
    else:
        form = HospitalForm(instance=hospital)
    
    return render(request, hospital/form.html', {
        'form': form,
        'title': 'Editar Hospital',
        'action': 'Atualizar',
        'hospital': hospital
    })

@login_required
def hospital_delete(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    
    if request.method == 'POST':
        hospital.delete()
        messages.success(request, 'Hospital excluído com sucesso!')
        return redirect('hospital_list')
    
    return render(request, hospital/confirm_delete.html', {
        'hospital': hospital
    })