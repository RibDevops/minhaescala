# views/tipo_evento_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from ..models import TipoEvento
from ..forms import TipoEventoForm


@login_required
def tipo_evento_list(request):
    tipos = TipoEvento.objects.all().order_by('codigo')
    
    paginator = Paginator(tipos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'cal/tipo_evento_list.html', {
        'page_obj': page_obj,
        'total_count': tipos.count()
    })

@login_required
def tipo_evento_create(request):
    if request.method == 'POST':
        form = TipoEventoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de Evento criado com sucesso!')
            return redirect('tipo_evento_list')
    else:
        form = TipoEventoForm()
    
    return render(request, 'tipo_evento/form.html', {
        'form': form,
        'title': 'Novo Tipo de Evento',
        'action': 'Criar'
    })

@login_required
def tipo_evento_update(request, pk):
    tipo = get_object_or_404(TipoEvento, pk=pk)
    
    if request.method == 'POST':
        form = TipoEventoForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de Evento atualizado com sucesso!')
            return redirect('tipo_evento_list')
    else:
        form = TipoEventoForm(instance=tipo)
    
    return render(request, 'tipo_evento/form.html', {
        'form': form,
        'title': 'Editar Tipo de Evento',
        'action': 'Atualizar'
    })

@login_required
def tipo_evento_delete(request, pk):
    tipo = get_object_or_404(TipoEvento, pk=pk)
    
    if request.method == 'POST':
        tipo.delete()
        messages.success(request, 'Tipo de Evento excluído com sucesso!')
        return redirect('tipo_evento_list')
    
    return render(request, 'tipo_evento/confirm_delete.html', {
        'tipo': tipo
    })