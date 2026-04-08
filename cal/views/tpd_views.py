# tpd_views.py - removido (lançamentos de TPD desativados)
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def listar_tpd(request):
    messages.info(request, "Módulo TPD foi desativado.")
    return redirect('cal:listar_eventos')


@login_required
def novo_tpd(request):
    messages.info(request, "Módulo TPD foi desativado.")
    return redirect('cal:listar_eventos')


@login_required
def excluir_tpd(request, pk):
    messages.info(request, "Módulo TPD foi desativado.")
    return redirect('cal:listar_eventos')


@login_required
def relatorio_mensal(request):
    messages.info(request, "Módulo TPD foi desativado.")
    return redirect('cal:listar_eventos')
