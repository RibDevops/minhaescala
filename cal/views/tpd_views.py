from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import models
from datetime import datetime

from ..models import TPD, Matricula, LIMITE_HORAS_MENSAIS_TPD
from ..forms import TPDForm


def _get_perfil(user):
    return getattr(user, 'cal_perfil', None)


def _matricula_do_usuario(user):
    return getattr(user, 'matricula', None)


def _tpd_queryset_para_usuario(user):
    """
    ADMIN/is_staff → todos os TPDs.
    ESCALANTE      → TPDs do seu hospital + setor.
    ENFERMEIRO     → TPDs do próprio profissional.
    """
    perfil = _get_perfil(user)
    if user.is_staff or (perfil and perfil.tipo == 'ADMIN'):
        return TPD.objects.all()

    matricula = _matricula_do_usuario(user)
    if not matricula:
        return TPD.objects.none()

    if perfil and perfil.tipo == 'ESCALANTE':
        return TPD.objects.filter(
            hospital=matricula.hospital,
            setor=matricula.setor,
        )

    # ENFERMEIRO — só os seus
    return TPD.objects.filter(profissional=matricula)


# ---------------------------------------------------------------------------
# Lista
# ---------------------------------------------------------------------------

@login_required
def listar_tpd(request):
    mes_filtro = request.GET.get('mes', '')
    profissional_filtro = request.GET.get('profissional', '')

    tpd_list = _tpd_queryset_para_usuario(request.user)

    if mes_filtro:
        tpd_list = tpd_list.filter(data__month=mes_filtro)

    if profissional_filtro:
        tpd_list = tpd_list.filter(profissional_id=profissional_filtro)

    paginator = Paginator(tpd_list.order_by('-data'), 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    total_horas = tpd_list.aggregate(total=models.Sum('horas_trabalhadas'))['total'] or 0

    meses = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'),
        (4, 'Abril'), (5, 'Maio'), (6, 'Junho'),
        (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'),
        (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
    ]

    perfil = _get_perfil(request.user)
    matricula = _matricula_do_usuario(request.user)
    if request.user.is_staff or (perfil and perfil.tipo == 'ADMIN'):
        profissionais = Matricula.objects.filter(ativo=True)
    elif perfil and perfil.tipo == 'ESCALANTE' and matricula:
        profissionais = Matricula.objects.filter(
            hospital=matricula.hospital,
            setor=matricula.setor,
            ativo=True,
        )
    else:
        profissionais = Matricula.objects.none()

    context = {
        'tpd_list': page_obj,
        'total_tpd': tpd_list.count(),
        'horas_mes': total_horas,
        'mes_filtro': mes_filtro,
        'prof_filtro': int(profissional_filtro) if profissional_filtro else '',
        'meses': meses,
        'profissionais': profissionais,
        'pode_criar': request.user.is_staff or (perfil and perfil.tipo in ('ADMIN', 'ESCALANTE')),
    }
    return render(request, 'tpd/listar_tpd.html', context)


# ---------------------------------------------------------------------------
# Criar
# ---------------------------------------------------------------------------

@login_required
def novo_tpd(request):
    perfil = _get_perfil(request.user)
    if not (request.user.is_staff or (perfil and perfil.tipo in ('ADMIN', 'ESCALANTE'))):
        raise PermissionDenied

    if request.method == 'POST':
        form = TPDForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                tpd = form.save(commit=False)
                tpd.criado_por = request.user
                tpd.save()
                messages.success(
                    request,
                    f"TPD registrado com sucesso! Total: {tpd.horas_trabalhadas:.1f}h"
                )
                return redirect('cal:listar_tpd')
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = TPDForm(user=request.user)

    return render(request, 'tpd/novo_tpd.html', {
        'form': form,
        'limite_mensal': LIMITE_HORAS_MENSAIS_TPD,
    })


# ---------------------------------------------------------------------------
# Excluir
# ---------------------------------------------------------------------------

@login_required
def excluir_tpd(request, pk):
    tpd = get_object_or_404(TPD, pk=pk)
    perfil = _get_perfil(request.user)

    if not request.user.is_staff and not (perfil and perfil.tipo == 'ADMIN'):
        matricula = _matricula_do_usuario(request.user)
        if not (
            perfil and perfil.tipo == 'ESCALANTE'
            and matricula
            and tpd.hospital == matricula.hospital
            and tpd.setor == matricula.setor
        ):
            raise PermissionDenied

    if request.method == 'POST':
        tpd.delete()
        messages.success(request, "TPD excluído com sucesso.")
        return redirect('cal:listar_tpd')

    return render(request, 'tpd/confirmar_exclusao.html', {'tpd': tpd})


# ---------------------------------------------------------------------------
# Relatório mensal
# ---------------------------------------------------------------------------

@login_required
def relatorio_mensal(request):
    mes = request.GET.get('mes', datetime.now().month)
    profissional_filtro = request.GET.get('profissional', '')

    tpd_mes = _tpd_queryset_para_usuario(request.user).filter(data__month=mes)

    if profissional_filtro:
        tpd_mes = tpd_mes.filter(profissional_id=profissional_filtro)

    total_horas = tpd_mes.aggregate(total=models.Sum('horas_trabalhadas'))['total'] or 0
    total_adicional_tpd = tpd_mes.aggregate(total=models.Sum('adicional_tpd'))['total'] or 0

    horas_por_profissional = []
    for prof in Matricula.objects.filter(tpds__data__month=mes).distinct():
        horas_prof = (
            tpd_mes.filter(profissional=prof)
            .aggregate(total=models.Sum('horas_trabalhadas'))['total'] or 0
        )
        if horas_prof > 0:
            percentual = float(horas_prof) / float(total_horas) * 100 if total_horas else 0
            horas_por_profissional.append({
                'nome': prof.nome_exibicao,
                'matricula': prof.matricula,
                'total_horas': horas_prof,
                'percentual': percentual,
                'percentual_grafico': min(percentual, 100),
                'excedeu': horas_prof > LIMITE_HORAS_MENSAIS_TPD,
            })
    horas_por_profissional.sort(key=lambda x: x['total_horas'], reverse=True)

    meses = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'),
        (4, 'Abril'), (5, 'Maio'), (6, 'Junho'),
        (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'),
        (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
    ]

    perfil = _get_perfil(request.user)
    matricula = _matricula_do_usuario(request.user)
    if request.user.is_staff or (perfil and perfil.tipo == 'ADMIN'):
        profissionais = Matricula.objects.filter(ativo=True)
    elif perfil and perfil.tipo == 'ESCALANTE' and matricula:
        profissionais = Matricula.objects.filter(
            hospital=matricula.hospital,
            setor=matricula.setor,
            ativo=True,
        )
    else:
        profissionais = Matricula.objects.none()

    context = {
        'tpd_mes': tpd_mes.order_by('data'),
        'total_tpds': tpd_mes.count(),
        'total_horas': total_horas,
        'total_adicional_tpd': total_adicional_tpd,
        'mes': mes,
        'meses': meses,
        'ano_atual': datetime.now().year,
        'horas_por_profissional': horas_por_profissional,
        'profissionais': profissionais,
        'profissional_filtro': int(profissional_filtro) if profissional_filtro else '',
        'limite_mensal': LIMITE_HORAS_MENSAIS_TPD,
    }
    return render(request, 'tpd/relatorio_mensal.html', context)
