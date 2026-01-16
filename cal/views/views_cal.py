import calendar
from datetime import datetime, timedelta, date
from django.shortcuts import render
from django.views import generic
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from cal.models import Transacao
from cal.utils import Calendar

def get_date(req_month):
    if req_month:
        year, month = (int(x) for x in req_month.split('-'))
        return date(year, month, 1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    return f'month={prev_month.year}-{prev_month.month}'


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    return f'month={next_month.year}-{next_month.month}'




@method_decorator(login_required, name='dispatch')


class CalendarView(generic.ListView):
    model = Transacao
    template_name = 'cal/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        d = get_date(self.request.GET.get('month'))  # mês atual

        user = self.request.user

        # ==================== MÊS ATUAL ====================
        transacoes_mes_atual = Transacao.objects.filter(
            user=user,
            data__year=d.year,
            data__month=d.month
        )
        # print(transacoes_mes_atual)

        total_creditos = transacoes_mes_atual.filter(tipo__codigo='C').aggregate(total=Sum('valor'))['total'] or 0
        total_debitos = transacoes_mes_atual.filter(tipo__codigo='D').aggregate(total=Sum('valor'))['total'] or 0
        saldo_total = total_creditos - total_debitos

        # ==================== PRÓXIMO MÊS ====================
        if d.month == 12:
            proximo_ano = d.year + 1
            proximo_mes = 1
        else:
            proximo_ano = d.year
            proximo_mes = d.month + 1

        transacoes_prox_mes = Transacao.objects.filter(
            user=user,
            data__year=proximo_ano,
            data__month=proximo_mes
        )
        # print(transacoes_prox_mes)
        total_creditos_prox = transacoes_prox_mes.filter(tipo__codigo='C').aggregate(total=Sum('valor'))['total'] or 0
        # print(total_creditos_prox)
        total_debitos_prox = transacoes_prox_mes.filter(tipo__codigo='D').aggregate(total=Sum('valor'))['total'] or 0
        # print(total_debitos_prox)
        saldo_total_prox = total_creditos_prox - total_debitos_prox
        # print(saldo_total_prox)


        # ==================== CALENDÁRIO HTML ====================
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True, transacoes=transacoes_mes_atual)

        # Datas para o btn-group padrão
        mes_atual_date = date(d.year, d.month, 1)
        mes_anterior_date = mes_atual_date - relativedelta(months=1)
        mes_proximo_date = mes_atual_date + relativedelta(months=1)

        context.update({
            'calendar': mark_safe(html_cal),
            'prev_month': prev_month(d),
            'next_month': next_month(d),
            'month_name': d.strftime("%B"),
            'year': d.year,
            'total_creditos': total_creditos,
            'total_debitos': total_debitos,
            'saldo_total': saldo_total,
            
            # Adiciona datas para o novo btn-group
            'mes_atual': mes_atual_date,
            'mes_anterior': mes_anterior_date,
            'mes_proximo': mes_proximo_date,

            # Adiciona dados do próximo mês
            'saldo_total_prox': saldo_total_prox,
            'total_creditos_prox': total_creditos_prox,
            'total_debitos_prox': total_debitos_prox,
            'mes_proximo_nome': date(proximo_ano, proximo_mes, 1).strftime("%B"),
        })

        return context



