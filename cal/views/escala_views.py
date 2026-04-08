# escala_views.py - simplificado (importação Excel removida)
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def lista_escalas(request):
    messages.info(request, "Funcionalidade de escala por arquivo removida.")
    return redirect('cal:escala_mensal')


@login_required
def importar_escala(request):
    messages.info(request, "Importação de escala por arquivo foi removida.")
    return redirect('cal:escala_mensal')


@login_required
def detalhes_escala(request, escala_id):
    return redirect('cal:escala_mensal')


@login_required
def relatorio_semanal(request, escala_id):
    return redirect('cal:escala_mensal')


@login_required
def exportar_escala(request, escala_id):
    messages.info(request, "Exportação por arquivo foi removida.")
    return redirect('cal:escala_mensal')


@login_required
def dashboard_escala(request):
    return redirect('cal:escala_mensal')


@login_required
def api_saldo_semanal(request, profissional_id, mes, ano):
    from django.http import JsonResponse
    return JsonResponse({'saldo': 'indisponível'})
