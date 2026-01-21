from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from ..models import Matricula

@login_required
def perfil_list(request):
    if not request.user.is_staff:
        messages.error(request, "Acesso negado.")
        return redirect('cal:home')
    
    matriculas = Matricula.objects.all().select_related('user', 'hospital', 'setor').order_by('nome_completo')
    paginator = Paginator(matriculas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'perfil/list.html', {
        'page_obj': page_obj,
        'total_count': matriculas.count()
    })
