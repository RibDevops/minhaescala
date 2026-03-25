# escala_mes_views.py
import os
os.environ["RL_NO_PIL"] = "1"



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from datetime import datetime, date, timedelta
from calendar import monthrange, day_name, month_name
import calendar
from ..models import (
    Matricula, EventoEscala, EscalaMensal, DiaEscala,
    ControleSemanal, TipoEvento, Hospital, Setor, PerfilUsuario
)
from ..permissions import get_matricula, is_admin, is_escalante, exige_escalante_ou_admin
from ..utils_saldo import saldo_info
from django.http import HttpResponse, JsonResponse
import io
import json
import logging

logger = logging.getLogger(__name__)

@login_required
def escala_mes_view(request, mes=None, ano=None):
    """
    View principal para exibir escala mensal dinâmica baseada nos plantões (EventoEscala)
    """
    hoje = datetime.now()
    mes = int(mes) if mes else hoje.month
    ano = int(ano) if ano else hoje.year

    hospital_id = request.GET.get('hospital')
    setor_id = request.GET.get('setor')
    
    user = request.user
    
    # Lógica de filtragem de profissionais
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
        # Usuário sem matrícula vinculada não tem acesso à escala
        profissionais = Matricula.objects.none()
        hospitais = Hospital.objects.none()
        setores = Setor.objects.none()

    if hospital_id: profissionais = profissionais.filter(hospital_id=hospital_id)
    if setor_id: profissionais = profissionais.filter(setor_id=setor_id)

    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])

    datas_cabecalho = []
    weekdays_pt = ['SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB', 'DOM']
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
        # Busca dinâmica: Eventos reais do calendário
        # Corrigido select_related: o campo é 'tipo' e não 'tipo_evento'
        eventos = EventoEscala.objects.filter(
            profissional=profissional,
            data__range=[primeiro_dia, ultimo_dia]
        ).select_related('tipo')

        dias_dict = {}
        for evento in eventos:
            codigo = ""
            horas = 0
            if evento.tipo:
                codigo = evento.tipo.codigo
                horas = float(evento.tipo.horas or 0)
            
            dias_dict[evento.data.day] = {
                'turnos': codigo,
                'horas': horas,
                'e_tpd': 'TPD' in codigo.upper()
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

        dados_profissionais.append({
            'profissional': profissional,
            'dias': dias_dict,
            'semanas_totais': semanas_totais,
            'total_mes': sum(d['horas'] for d in dias_dict.values()),
            'saldo': saldo_info(profissional, mes, ano),
        })

    meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
    
    context = {
        'mes_atual': mes, 'ano_atual': ano, 'mes_nome': meses_pt[mes],
        'dados_profissionais': dados_profissionais, 'datas_cabecalho': datas_cabecalho,
        'hospitais': hospitais, 'setores': setores,
        'hospital_filtro': int(hospital_id) if hospital_id else None,
        'setor_filtro': int(setor_id) if setor_id else None,
        'num_semanas': range(1, semana_atual),
        'mes_anterior': {'mes': 12 if mes==1 else mes-1, 'ano': ano-1 if mes==1 else ano, 'nome': meses_pt[12 if mes==1 else mes-1]},
        'mes_proximo': {'mes': 1 if mes==12 else mes+1, 'ano': ano+1 if mes==12 else ano, 'nome': meses_pt[1 if mes==12 else mes+1]},
    }
    return render(request, 'escala/escala_mes.html', context)

@login_required
def toggle_dia_escala(request, profissional_id, dia, mes, ano):
    """
    API para salvar plantão vindo da escala mensal.
    Somente escalante (do mesmo setor) ou admin pode alterar.
    """
    if not is_admin(request.user) and not is_escalante(request.user):
        return JsonResponse({'success': False, 'error': 'Sem permissão'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profissional = get_object_or_404(Matricula, id=profissional_id)

            # Escalante só pode alterar profissionais do seu setor
            if is_escalante(request.user):
                matricula_usuario = get_matricula(request.user)
                if not matricula_usuario or profissional.hospital != matricula_usuario.hospital or profissional.setor != matricula_usuario.setor:
                    return JsonResponse({'success': False, 'error': 'Sem permissão para este setor'}, status=403)

            data_plantao = date(int(ano), int(mes), int(dia))
            
            # Remove eventos existentes no dia para este profissional
            EventoEscala.objects.filter(profissional=profissional, data=data_plantao).delete()
            
            if data.get('turno'):
                tipo_evento = TipoEvento.objects.filter(codigo=data['turno']).first()
                if tipo_evento:
                    # O campo correto no modelo EventoEscala é 'tipo' e não 'tipo_evento'
                    # Além disso, o modelo exige hospital e setor, que pegamos da matrícula do profissional
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
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
    except ImportError as e:
        logger.error(f"Erro ao importar ReportLab: {e}")
        return HttpResponse("Erro técnico: O sistema de geração de PDF não está disponível no momento devido a falhas em bibliotecas do servidor.", status=500)

    hospital_id = request.GET.get('hospital')
    setor_id = request.GET.get('setor')
    
    mes, ano = int(mes), int(ano)
    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])
    
    profissionais = Matricula.objects.filter(ativo=True)
    if hospital_id: profissionais = profissionais.filter(hospital_id=hospital_id)
    if setor_id: profissionais = profissionais.filter(setor_id=setor_id)

    buffer = io.BytesIO()
    try:
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=10, leftMargin=10, topMargin=20, bottomMargin=20)
        elements = []
        styles = getSampleStyleSheet()
        
        h_nome = Hospital.objects.get(id=hospital_id).nome if hospital_id else "Geral"
        titulo = f"Escala Mensal - {h_nome} ({mes}/{ano})"
        elements.append(Paragraph(titulo, styles['Title']))
        
        num_dias = monthrange(ano, mes)[1]
        header = ['Profissional'] + [str(d) for d in range(1, num_dias + 1)] + ['Total']
        table_data = [header]

        for prof in profissionais:
            nome = prof.nome_exibicao or (prof.nome_completo[:15] if prof.nome_completo else "Sem Nome")
            linha = [nome]
            total_horas = 0
            # Corrigido select_related para 'tipo'
            eventos = EventoEscala.objects.filter(profissional=prof, data__range=[primeiro_dia, ultimo_dia]).select_related('tipo')
            dias_dict = {e.data.day: (e.tipo.codigo if e.tipo else "") for e in eventos}
            horas_dict = {e.data.day: (float(e.tipo.horas or 0) if e.tipo else 0) for e in eventos}

            for d in range(1, num_dias + 1):
                turno = dias_dict.get(d, '-')
                linha.append(turno)
                total_horas += horas_dict.get(d, 0)
            
            linha.append(f"{int(total_horas)}h")
            table_data.append(linha)

        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ]))
        elements.append(t)
        doc.build(elements)
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=escala_{mes}_{ano}.pdf'
        return response
    except Exception as e:
        logger.exception("Erro durante a geração do PDF")
        if "PIL" in str(e) or "_imaging" in str(e):
             return HttpResponse("Erro de compatibilidade: O servidor não consegue processar o PDF agora devido a uma falha na biblioteca de imagens. Tente novamente mais tarde.", status=500)
        return HttpResponse(f"Erro ao gerar PDF: {str(e)}", status=500)

@login_required
def escala_create(request):
    mes = request.POST.get('mes')
    ano = request.POST.get('ano')
    return redirect('cal:escala_mensal_mes_ano', mes=mes, ano=ano)

@login_required
def importar_escala_excel(request):
    """
    Função de fallback para importação de excel.
    """
    messages.info(request, "Funcionalidade de importação em desenvolvimento.")
    return redirect('cal:escala_mensal')
