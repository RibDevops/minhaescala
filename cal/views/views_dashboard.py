from django.shortcuts import render
from ..models import Plantao, Enfermeiro, Hospital, Setor
from django.db.models import Count, Sum
from django.contrib.auth.decorators import login_required
from datetime import date
import calendar

@login_required
def dashboard(request):
    user = request.user
    hoje = date.today()
    mes_selecionado = int(request.GET.get('mes', hoje.month))
    ano_selecionado = int(request.GET.get('ano', hoje.year))
    
    plantoes_base = Plantao.objects.filter(
        data__year=ano_selecionado,
        data__month=mes_selecionado
    )
    
    if not user.is_staff and not (hasattr(user, 'perfil') and user.perfil.tipo_usuario in ['ESCALANTE', 'CHEFE', 'ADMIN']):
        if hasattr(user, 'perfil') and hasattr(user.perfil, 'enfermeiro'):
            plantoes_base = plantoes_base.filter(enfermeiro=user.perfil.enfermeiro)
        else:
            plantoes_base = plantoes_base.none()

    total_plantoes = plantoes_base.count()
    total_horas = plantoes_base.aggregate(total=Sum('tipo_plantao__horas'))['total'] or 0
    
    # Distribuição por Tipo de Plantão
    por_tipo = plantoes_base.values('tipo_plantao__codigo').annotate(total=Count('id')).order_by('-total')
    
    # Dados para Gráficos
    # 1. Profissionais por Dia
    profissionais_por_dia = list(plantoes_base.values('data__day').annotate(total=Count('enfermeiro', distinct=True)).order_by('data__day'))
    
    # 2. Profissionais por Turno (Período)
    profissionais_por_turno = list(plantoes_base.values('tipo_plantao__periodo').annotate(total=Count('enfermeiro', distinct=True)))
    
    # Mapeamento de períodos para nomes amigáveis
    periodo_map = dict(Plantao.tipo_plantao.field.related_model.PERIODO_CHOICES)
    for item in profissionais_por_turno:
        item['periodo_nome'] = periodo_map.get(item['tipo_plantao__periodo'], item['tipo_plantao__periodo'])

    # Top Profissionais (se tiver permissão)
    top_profissionais = None
    if user.is_staff or (hasattr(user, 'perfil') and user.perfil.tipo_usuario != 'PROFISSIONAL'):
        top_profissionais = plantoes_base.values('enfermeiro__nome').annotate(
            total=Count('id'),
            horas=Sum('tipo_plantao__horas')
        ).order_by('-horas')[:5]

    anos_disponiveis = range(hoje.year - 2, hoje.year + 2)
    meses_disponiveis = [
        (i, calendar.month_name[i].capitalize()) for i in range(1, 13)
    ]

    return render(request, 'cal/dashboard.html', {
        'mes_selecionado': mes_selecionado,
        'ano_selecionado': ano_selecionado,
        'anos_disponiveis': anos_disponiveis,
        'meses_disponiveis': meses_disponiveis,
        'total_plantoes': total_plantoes,
        'total_horas': total_horas,
        'por_tipo': por_tipo,
        'top_profissionais': top_profissionais,
        'grafico_dias_labels': [item['data__day'] for item in profissionais_por_dia],
        'grafico_dias_valores': [item['total'] for item in profissionais_por_dia],
        'grafico_turnos_labels': [item['periodo_nome'] for item in profissionais_por_turno],
        'grafico_turnos_valores': [item['total'] for item in profissionais_por_turno],
    })
