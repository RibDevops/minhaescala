from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from datetime import datetime
from ..models import TPD, Matricula
from ..forms import TPDForm

def listar_tpd(request):
    """Lista todos os TPDs com filtros"""
    mes_filtro = request.GET.get('mes', '')
    profissional_filtro = request.GET.get('profissional', '')
    status_filtro = request.GET.get('status', '')

    tpd_list = TPD.objects.all()

    if mes_filtro:
        tpd_list = tpd_list.filter(data__month=mes_filtro)

    if profissional_filtro:
        tpd_list = tpd_list.filter(profissional_id=profissional_filtro)

    if status_filtro == 'com_problema':
        tpd_list = tpd_list.filter(violacao_regra=True)
    elif status_filtro == 'sem_problema':
        tpd_list = tpd_list.filter(violacao_regra=False)

    paginator = Paginator(tpd_list.order_by('-data'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_tpd = tpd_list.count()
    tpd_com_problema = tpd_list.filter(violacao_regra=True).count()

    mes_atual = datetime.now().month
    horas_mes = sum(t.horas_trabalhadas for t in tpd_list if t.data.month == mes_atual)

    meses = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'),
        (4, 'Abril'), (5, 'Maio'), (6, 'Junho'),
        (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'),
        (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]

    context = {
        'tpd_list': page_obj,
        'total_tpd': total_tpd,
        'tpd_com_problema': tpd_com_problema,
        'horas_mes': horas_mes,
        'mes_filtro': mes_filtro,
        'prof_filtro': int(profissional_filtro) if profissional_filtro else '',
        'status_filtro': status_filtro,
        'meses': meses,
        'profissionais': Matricula.objects.all(),
    }
    return render(request, 'tpd/listar_tpd.html', context)

def novo_tpd(request):
    if request.method == 'POST':
        form = TPDForm(request.POST)
        if form.is_valid():
            tpd = form.save()
            if tpd.violacao_regra:
                messages.warning(request, f"TPD registrado com ALERTA: {tpd.mensagem_erro}")
            else:
                messages.success(request, f"TPD registrado com sucesso! Total: {tpd.horas_trabalhadas}h")
            return redirect('cal:listar_tpd')
    else:
        form = TPDForm()
    return render(request, 'tpd/novo_tpd.html', {'form': form})

def relatorio_mensal(request):
    mes = request.GET.get('mes', datetime.now().month)
    profissional_filtro = request.GET.get('profissional', '')
    tpd_mes = TPD.objects.filter(data__month=mes)

    if profissional_filtro:
        tpd_mes = tpd_mes.filter(profissional_id=profissional_filtro)

    total_tpds = tpd_mes.count()
    total_horas = sum(t.horas_trabalhadas for t in tpd_mes)
    total_noturnas = sum(t.horas_noturnas for t in tpd_mes)
    total_adicional_tpd = sum(t.adicional_tpd for t in tpd_mes)
    total_adicional_noturno = sum(t.adicional_noturno for t in tpd_mes)
    total_geral = total_adicional_tpd + total_adicional_noturno
    violacoes = tpd_mes.filter(violacao_regra=True).count()

    horas_por_profissional = []
    for prof in Matricula.objects.all():
        horas_prof = tpd_mes.filter(profissional=prof).aggregate(total=models.Sum('horas_trabalhadas'))['total'] or 0
        if horas_prof > 0:
            percentual = (horas_prof / total_horas * 100) if total_horas > 0 else 0
            horas_por_profissional.append({
                'nome': prof.nome_exibicao,
                'matricula': prof.matricula,
                'total_horas': horas_prof,
                'percentual': percentual,
            })
    horas_por_profissional.sort(key=lambda x: x['total_horas'], reverse=True)

    context = {
        'tpd_mes': tpd_mes.order_by('data'),
        'total_tpds': total_tpds,
        'total_horas': total_horas,
        'total_noturnas': total_noturnas,
        'violacoes': violacoes,
        'mes': mes,
        'total_geral': total_geral,
        'horas_por_profissional': horas_por_profissional,
    }
    return render(request, 'tpd/relatorio_mensal.html', context)

def dashboard(request):
    ultimos_tpd = TPD.objects.all().order_by('-data')[:10]
    total_tpds = TPD.objects.count()
    total_horas = TPD.objects.aggregate(total=models.Sum('horas_trabalhadas'))['total'] or 0
    context = {
        'ultimos_tpd': ultimos_tpd,
        'total_tpds': total_tpds,
        'total_horas': total_horas,
    }
    return render(request, 'tpd/dashboard.html', context)
