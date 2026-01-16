from django.shortcuts import render
from ..models import Plantao
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from datetime import date
from collections import OrderedDict

@login_required
def dashboard(request):
    user = request.user
    hoje = date.today()
    ano_selecionado = int(request.GET.get('ano', hoje.year))
    
    # Exemplo simplificado de dashboard para Plantões
    plantoes_ano = Plantao.objects.filter(
        data__year=ano_selecionado
    )
    
    if not user.is_staff:
        if hasattr(user, 'perfil') and hasattr(user.perfil, 'enfermeiro'):
            plantoes_ano = plantoes_ano.filter(enfermeiro=user.perfil.enfermeiro)
        else:
            plantoes_ano = plantoes_ano.none()

    total_plantoes = plantoes_ano.count()

    anos_disponiveis = range(hoje.year - 5, hoje.year + 2)

    return render(request, 'cal/dashboard.html', {
        'ano_selecionado': ano_selecionado,
        'anos_disponiveis': anos_disponiveis,
        'total_plantoes': total_plantoes,
    })
