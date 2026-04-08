# escala_mes_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, date, timedelta
from calendar import monthrange
import json
import logging

from ..models import Matricula, EventoEscala, TipoEvento, Hospital, Setor
from ..permissions import get_matricula, is_admin, is_escalante, exige_escalante_ou_admin
from ..utils_saldo import saldo_info
from django.http import HttpResponse, JsonResponse

logger = logging.getLogger(__name__)

MESES_PT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}


@login_required
def escala_mes_view(request, mes=None, ano=None):
    hoje = datetime.now()
    mes = int(mes) if mes else hoje.month
    ano = int(ano) if ano else hoje.year

    hospital_id = request.GET.get('hospital')
    setor_id = request.GET.get('setor')

    user = request.user
    matricula_usuario = get_matricula(user)

    if is_admin(user):
        profissionais = Matricula.objects.filter(ativo=True)
        hospitais = Hospital.objects.all()
        setores = Setor.objects.all()
    elif matricula_usuario:
        profissionais = Matricula.objects.filter(
            hospital=matricula_usuario.hospital,
            setor=matricula_usuario.setor,
            ativo=True
        )
        hospitais = Hospital.objects.filter(id=matricula_usuario.hospital.id)
        setores = Setor.objects.filter(id=matricula_usuario.setor.id)
        if not hospital_id:
            hospital_id = matricula_usuario.hospital.id
        if not setor_id:
            setor_id = matricula_usuario.setor.id
    else:
        profissionais = Matricula.objects.none()
        hospitais = Hospital.objects.none()
        setores = Setor.objects.none()

    if hospital_id:
        profissionais = profissionais.filter(hospital_id=hospital_id)
    if setor_id:
        profissionais = profissionais.filter(setor_id=setor_id)

    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])

    weekdays_pt = ['SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB', 'DOM']
    datas_cabecalho = []
    for dia in range(1, ultimo_dia.day + 1):
        data_dia = date(ano, mes, dia)
        datas_cabecalho.append({
            'dia': dia,
            'dia_semana': weekdays_pt[data_dia.weekday()],
            'data_completa': data_dia,
            'weekday_idx': data_dia.weekday()
        })

    dados_profissionais = []
    semana_atual = 1

    for profissional in profissionais:
        eventos = EventoEscala.objects.filter(
            profissional=profissional,
            data__range=[primeiro_dia, ultimo_dia]
        ).select_related('tipo')

        dias_dict = {}
        for evento in eventos:
            codigo = ''
            horas = 0
            cor = '#3498db'
            if evento.tipo:
                codigo = evento.tipo.codigo
                horas = float(evento.tipo.horas or 0)
                cor = evento.tipo.cor or '#3498db'
            if hasattr(evento, 'cor') and evento.cor:
                cor = evento.cor
            dias_dict[evento.data.day] = {
                'turnos': codigo,
                'horas': horas,
                'cor': cor,
                'evento_id': evento.id,
            }

        semanas_totais = {}
        semana_idx = 1
        current_week_hours = 0
        for dia_idx, data_head in enumerate(datas_cabecalho):
            dia = data_head['dia']
            if dia in dias_dict:
                current_week_hours += dias_dict[dia]['horas']
            if data_head['weekday_idx'] == 6 or dia_idx == len(datas_cabecalho) - 1:
                semanas_totais[semana_idx] = current_week_hours
                semana_idx += 1
                current_week_hours = 0

        if semana_idx > semana_atual:
            semana_atual = semana_idx

        total_mes = sum(d['horas'] for d in dias_dict.values())
        dados_profissionais.append({
            'profissional': profissional,
            'dias': dias_dict,
            'semanas_totais': semanas_totais,
            'total_mes': total_mes,
            'saldo': saldo_info(profissional, mes, ano, total_horas=total_mes),
        })

    context = {
        'mes_atual': mes,
        'ano_atual': ano,
        'mes_nome': MESES_PT[mes],
        'dados_profissionais': dados_profissionais,
        'datas_cabecalho': datas_cabecalho,
        'hospitais': hospitais,
        'setores': setores,
        'hospital_filtro': int(hospital_id) if hospital_id else None,
        'setor_filtro': int(setor_id) if setor_id else None,
        'num_semanas': range(1, semana_atual),
        'mes_anterior': {
            'mes': 12 if mes == 1 else mes - 1,
            'ano': ano - 1 if mes == 1 else ano,
            'nome': MESES_PT[12 if mes == 1 else mes - 1]
        },
        'mes_proximo': {
            'mes': 1 if mes == 12 else mes + 1,
            'ano': ano + 1 if mes == 12 else ano,
            'nome': MESES_PT[1 if mes == 12 else mes + 1]
        },
    }
    return render(request, 'escala/escala_mes.html', context)


@login_required
def toggle_dia_escala(request, profissional_id, dia, mes, ano):
    if not is_admin(request.user) and not is_escalante(request.user):
        return JsonResponse({'success': False, 'error': 'Sem permissão'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profissional = get_object_or_404(Matricula, id=profissional_id)

            if is_escalante(request.user):
                matricula_usuario = get_matricula(request.user)
                if not matricula_usuario or profissional.hospital != matricula_usuario.hospital or profissional.setor != matricula_usuario.setor:
                    return JsonResponse({'success': False, 'error': 'Sem permissão para este setor'}, status=403)

            data_plantao = date(int(ano), int(mes), int(dia))
            EventoEscala.objects.filter(profissional=profissional, data=data_plantao).delete()

            if data.get('turno'):
                tipo_evento = TipoEvento.objects.filter(codigo=data['turno']).first()
                if tipo_evento:
                    EventoEscala.objects.create(
                        profissional=profissional,
                        data=data_plantao,
                        tipo=tipo_evento,
                        hospital=profissional.hospital,
                        setor=profissional.setor,
                        criado_por=request.user
                    )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método inválido'})


@login_required
def exportar_escala_pdf(request, mes, ano):
    messages.info(request, "Exportação PDF foi desativada.")
    return redirect('cal:escala_mensal')


@login_required
def escala_create(request):
    mes = request.POST.get('mes')
    ano = request.POST.get('ano')
    return redirect('cal:escala_mensal_mes_ano', mes=mes, ano=ano)


@login_required
def importar_escala_excel(request):
    messages.info(request, "Funcionalidade de importação em desenvolvimento.")
    return redirect('cal:escala_mensal')
