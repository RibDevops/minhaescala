    # views.py - atualizado
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from django.core.paginator import Paginator
    from datetime import datetime
    from .models import TPD, Profissional
    from .forms import TPDForm

    def listar_tpd(request):
        """Lista todos os TPDs com filtros"""
        # Filtros
        mes_filtro = request.GET.get('mes', '')
        profissional_filtro = request.GET.get('profissional', '')
        status_filtro = request.GET.get('status', '')

        tpd_list = TPD.objects.all()

        # Aplicar filtros
        if mes_filtro:
            tpd_list = tpd_list.filter(data__month=mes_filtro)

        if profissional_filtro:
            tpd_list = tpd_list.filter(profissional_id=profissional_filtro)

        if status_filtro == 'com_problema':
            tpd_list = tpd_list.filter(violacao_regra=True)
        elif status_filtro == 'sem_problema':
            tpd_list = tpd_list.filter(violacao_regra=False)

        # Paginação
        paginator = Paginator(tpd_list.order_by('-data'), 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Estatísticas
        total_tpd = tpd_list.count()
        tpd_com_problema = tpd_list.filter(violacao_regra=True).count()

        # Horas do mês atual
        mes_atual = datetime.now().month
        horas_mes = sum(
            t.horas_trabalhadas for t in tpd_list 
            if t.data.month == mes_atual
        )

        # Dados para filtros
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
            'total_profissionais': Profissional.objects.count(),
            'mes_filtro': mes_filtro,
            'prof_filtro': int(profissional_filtro) if profissional_filtro else '',
            'status_filtro': status_filtro,
            'meses': meses,
            'profissionais': Profissional.objects.all(),
        }

        return render(request, 'listar_tpd.html', context)

    def relatorio_mensal(request):
        """Gera relatório mensal detalhado"""
        # Mês selecionado (padrão: mês atual)
        mes = request.GET.get('mes', datetime.now().month)
        profissional_filtro = request.GET.get('profissional', '')

        # Filtra TPDs do mês
        tpd_mes = TPD.objects.filter(data__month=mes)

        if profissional_filtro:
            tpd_mes = tpd_mes.filter(profissional_id=profissional_filtro)

        # Cálculos
        total_tpds = tpd_mes.count()
        total_horas = sum(t.horas_trabalhadas for t in tpd_mes)
        total_noturnas = sum(t.horas_noturnas for t in tpd_mes)

        # Valores
        total_adicional_tpd = sum(t.adicional_tpd for t in tpd_mes)
        total_adicional_noturno = sum(t.adicional_noturno for t in tpd_mes)
        total_geral = total_adicional_tpd + total_adicional_noturno

        # Violações
        violacoes = tpd_mes.filter(violacao_regra=True).count()
        lista_violacoes = list(tpd_mes.filter(violacao_regra=True).values_list('mensagem_erro', flat=True)[:5])

        # Horas por profissional
        profissionais = Profissional.objects.all()
        horas_por_profissional = []

        for prof in profissionais:
            horas_prof = tpd_mes.filter(profissional=prof).aggregate(
                total=models.Sum('horas_trabalhadas')
            )['total'] or 0

            if horas_prof > 0:
                percentual = (horas_prof / total_horas * 100) if total_horas > 0 else 0
                horas_por_profissional.append({
                    'nome': prof.nome,
                    'matricula': prof.matricula,
                    'total_horas': horas_prof,
                    'percentual': percentual,
                    'percentual_grafico': min(percentual * 2, 100)
                })

        # Ordena por horas
        horas_por_profissional.sort(key=lambda x: x['total_horas'], reverse=True)

        # Percentuais
        percentual_noturno = (total_noturnas / total_horas * 100) if total_horas > 0 else 0
        percentual_violacoes = (violacoes / total_tpds * 100) if total_tpds > 0 else 0
        media_horas = total_horas / 30 if total_horas > 0 else 0

        # Nome do mês
        meses_nomes = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }

        context = {
            'tpd_mes': tpd_mes.order_by('data'),
            'total_tpds': total_tpds,
            'total_horas': total_horas,
            'total_noturnas': total_noturnas,
            'violacoes': violacoes,
            'lista_violacoes': lista_violacoes,
            'mes': mes,
            'mes_nome': meses_nomes.get(int(mes), ''),
            'ano_atual': datetime.now().year,
            'profissionais': profissionais,
            'profissional_filtro': int(profissional_filtro) if profissional_filtro else '',
            'meses': list(meses_nomes.items()),

            # Financeiro
            'valor_base': total_horas * 50,  # R$ 50/hora base
            'total_adicional_tpd': total_adicional_tpd,
            'total_adicional_noturno': total_adicional_noturno,
            'total_geral': total_geral,

            # Estatísticas
            'horas_por_profissional': horas_por_profissional,
            'percentual_noturno': percentual_noturno,
            'percentual_violacoes': percentual_violacoes,
            'media_horas': media_horas,
        }

        return render(request, 'relatorio_mensal.html', context)