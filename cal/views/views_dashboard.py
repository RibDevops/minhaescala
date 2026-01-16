from django.shortcuts import render
from ..models import Transacao
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from datetime import date
from collections import OrderedDict

@login_required
def dashboard(request):
    user = request.user
    hoje = date.today()
    ano_selecionado = int(request.GET.get('ano', hoje.year))
    
    # Todos os meses do ano selecionado
    transacoes_ano = Transacao.objects.filter(
        user=user, 
        data__year=ano_selecionado
    ).select_related('tipo', 'categoria')

    # Resumo Anual
    credito_anual = transacoes_ano.filter(tipo__codigo='C').aggregate(total=Sum('valor'))['total'] or 0
    debito_anual = transacoes_ano.filter(tipo__codigo='D').aggregate(total=Sum('valor'))['total'] or 0
    saldo_anual = credito_anual - debito_anual

    # Detalhamento por Mês
    meses_detalhe = OrderedDict()
    nomes_meses = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    for mes_num in range(1, 13):
        transacoes_mes = transacoes_ano.filter(data__month=mes_num)
        
        c_mes = transacoes_mes.filter(tipo__codigo='C').aggregate(total=Sum('valor'))['total'] or 0
        d_mes = transacoes_mes.filter(tipo__codigo='D').aggregate(total=Sum('valor'))['total'] or 0
        s_mes = c_mes - d_mes
        
        # Dados para o gráfico do mês (por categoria)
        dados_grafico = (
            transacoes_mes.values('categoria__nome')
            .annotate(total=Sum('valor'))
            .order_by('-total')
        )
        
        meses_detalhe[mes_num] = {
            'nome': nomes_meses[mes_num],
            'credito': c_mes,
            'debito': d_mes,
            'saldo': s_mes,
            'grafico_labels': [item['categoria__nome'] or 'Sem Categoria' for item in dados_grafico],
            'grafico_valores': [float(item['total']) for item in dados_grafico],
            'tem_dados': transacoes_mes.exists()
        }

    anos_disponiveis = range(hoje.year - 5, hoje.year + 2)

    return render(request, 'cal/dashboard.html', {
        'ano_selecionado': ano_selecionado,
        'anos_disponiveis': anos_disponiveis,
        'credito_anual': credito_anual,
        'debito_anual': debito_anual,
        'saldo_anual': saldo_anual,
        'meses_detalhe': meses_detalhe,
    })
