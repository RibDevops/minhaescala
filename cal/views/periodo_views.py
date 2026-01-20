# escalas/views/periodo_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from ..models import Periodo
from ..forms import PeriodoForm

@login_required
def periodo_list(request):
    periodos = Periodo.objects.all().order_by('nome')
    
    paginator = Paginator(periodos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'escalas/periodo/list.html', {
        'page_obj': page_obj,
        'total_count': periodos.count()
    })

@login_required
def periodo_create(request):
    if request.method == 'POST':
        form = PeriodoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Período criado com sucesso!')
            return redirect('periodo_list')
    else:
        form = PeriodoForm()
    
    return render(request, 'escalas/periodo/form.html', {
        'form': form,
        'title': 'Novo Período',
        'action': 'Criar'
    })

@login_required
def periodo_update(request, pk):
    periodo = get_object_or_404(Periodo, pk=pk)
    
    if request.method == 'POST':
        form = PeriodoForm(request.POST, instance=periodo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Período atualizado com sucesso!')
            return redirect('periodo_list')
    else:
        form = PeriodoForm(instance=periodo)
    
    return render(request, 'escalas/periodo/form.html', {
        'form': form,
        'title': 'Editar Período',
        'action': 'Atualizar'
    })

@login_required
def periodo_delete(request, pk):
    periodo = get_object_or_404(Periodo, pk=pk)
    
    if request.method == 'POST':
        periodo.delete()
        messages.success(request, 'Período excluído com sucesso!')
        return redirect('periodo_list')
    
    return render(request, 'escalas/periodo/confirm_delete.html', {
        'periodo': periodo
    })