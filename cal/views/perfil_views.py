from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import PerfilUsuario
from ..forms import PerfilUsuarioForm

@login_required
def perfil_list(request):
    if not request.user.is_staff:
        messages.error(request, "Acesso negado.")
        return redirect('cal:home')
    
    perfis = PerfilUsuario.objects.all().select_related('user').prefetch_related('matriculas_vinculadas')
    return render(request, 'cal/perfil/list.html', {'perfis': perfis})

@login_required
def perfil_create(request):
    if not request.user.is_staff:
        messages.error(request, "Acesso negado.")
        return redirect('cal:home')
    
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil criado com sucesso.")
            return redirect('cal:perfil_list')
    else:
        form = PerfilUsuarioForm()
    
    return render(request, 'cal/perfil/form.html', {'form': form, 'title': 'Novo Perfil'})

@login_required
def perfil_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Acesso negado.")
        return redirect('cal:home')
    
    perfil = get_object_or_404(PerfilUsuario, pk=pk)
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso.")
            return redirect('cal:perfil_list')
    else:
        form = PerfilUsuarioForm(instance=perfil)
    
    return render(request, 'cal/perfil/form.html', {'form': form, 'title': 'Editar Perfil'})

@login_required
def perfil_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Acesso negado.")
        return redirect('cal:home')
    
    perfil = get_object_or_404(PerfilUsuario, pk=pk)
    if request.method == 'POST':
        perfil.delete()
        messages.success(request, "Perfil excluído com sucesso.")
        return redirect('cal:perfil_list')
    
    return render(request, 'cal/perfil/confirm_delete.html', {'perfil': perfil})
