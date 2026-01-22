from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import PerfilUsuario

@login_required
def perfil_list(request):
    if not request.user.is_staff:
        messages.error(request, "Acesso negado.")
        return redirect('cal:home')
    
    perfis = PerfilUsuario.objects.all().select_related('user').prefetch_related('matriculas_vinculadas')
    return render(request, 'cal/perfil/list.html', {'perfis': perfis})
