from django.shortcuts import render
from ..models import EventoEscala, Matricula, Hospital, Setor
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
    
    eventos_base = EventoEscala.objects.filter(
        data__year=ano_selecionado,
        data__month=mes_selecionado
    )
    
    if not user.is_staff and not (hasattr(user, 'perfil') and user.perfil.tipo_usuario in ['ESCALANTE', 'CHEFE', 'ADMIN']):
        if hasattr(user, 'perfil') and hasattr(user.perfil, 'matricula'):
            eventos_base = eventos_base.filter(profissional=user.perfil.matricula)
        else:
            eventos_base = eventos_base.none()

    total_plantoes = eventos_base.count()
    total_horas = eventos_base.aggregate(total=Sum('tipo_evento__horas'))['total'] or 0
    
    # Distribuição por Tipo de Evento
    por_tipo = eventos_base.values('tipo_evento__codigo').annotate(total=Count('id')).order_by('-total')
    
    # Dados para Gráficos
    profissionais_por_dia = list(eventos_base.values('data__day').annotate(total=Count('profissional', distinct=True)).order_by('data__day'))
    
    # Profissionais por Turno (Período)
    profissionais_por_turno = list(eventos_base.values('tipo_evento__periodo__nome').annotate(total=Count('profissional', distinct=True)))

    # Top Profissionais
    top_profissionais = None
    if user.is_staff or (hasattr(user, 'perfil') and user.perfil.tipo_usuario != 'PROFISSIONAL'):
        top_profissionais = eventos_base.values('profissional__nome_exibicao').annotate(
            total=Count('id'),
            horas=Sum('tipo_evento__horas')
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
        'grafico_turnos_labels': [item['tipo_evento__periodo__nome'] for item in profissionais_por_turno],
        'grafico_turnos_valores': [item['total'] for item in profissionais_por_turno],
    })
