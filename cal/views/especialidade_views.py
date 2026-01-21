from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from ..models import Especialidade
from ..forms import EspecialidadeForm

@login_required
def especialidade_list(request):
    especialidades = Especialidade.objects.all().order_by('nome')
    paginator = Paginator(especialidades, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'especialidade/list.html', {
        'page_obj': page_obj,
        'total_count': especialidades.count()
    })

@login_required
def especialidade_create(request):
    if request.method == 'POST':
        form = EspecialidadeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Especialidade criada com sucesso!')
            return redirect('cal:especialidade_list')
    else:
        form = EspecialidadeForm()
    return render(request, 'especialidade/form.html', {
        'form': form,
        'title': 'Nova Especialidade',
        'action': 'Criar'
    })

@login_required
def especialidade_update(request, pk):
    especialidade = get_object_or_404(Especialidade, pk=pk)
    if request.method == 'POST':
        form = EspecialidadeForm(request.POST, instance=especialidade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Especialidade atualizada com sucesso!')
            return redirect('cal:especialidade_list')
    else:
        form = EspecialidadeForm(instance=especialidade)
    return render(request, 'especialidade/form.html', {
        'form': form,
        'title': 'Editar Especialidade',
        'action': 'Atualizar'
    })

@login_required
def especialidade_delete(request, pk):
    especialidade = get_object_or_404(Especialidade, pk=pk)
    if request.method == 'POST':
        especialidade.delete()
        messages.success(request, 'Especialidade excluída com sucesso!')
        return redirect('cal:especialidade_list')
    return render(request, 'especialidade/confirm_delete.html', {'especialidade': especialidade})
