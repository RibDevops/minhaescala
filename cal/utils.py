from calendar import HTMLCalendar
from datetime import date
from .models import EventoEscala

MESES_PT = [
    '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

DIAS_SEMANA_PT = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, plantoes=None):
        self.year = year
        self.month = month
        self.plantoes = plantoes
        super(Calendar, self).__init__()

    def formatmonthname(self, theyear, themonth, withyear=True):
        nome_mes = MESES_PT[themonth]
        if withyear:
            s = f'{nome_mes} {theyear}'
        else:
            s = nome_mes
        return f'<tr><th colspan="7" class="month">{s}</th></tr>'

    def formatweekheader(self):
        s = ''.join(f'<th class="{self.cssclasses[i]}">{DIAS_SEMANA_PT[i]}</th>' for i in range(7))
        return f'<tr>{s}</tr>'

    def formatday(self, day, weekday):
        plantoes_do_dia = self.plantoes.filter(data__day=day)
        d = ''
        resumo_especialidade = {}
        
        for plantao in plantoes_do_dia:
            nome = plantao.profissional.nome_exibicao
            codigo = plantao.tipo.codigo if plantao.tipo else '—'
            horas = plantao.tipo.horas or 0 if plantao.tipo else 0
            cor = plantao.tipo.cor if plantao.tipo else '#999'
            observacao = plantao.observacao or ''
            obs_html = (
                f'<div style="font-size:0.78em; opacity:0.9; margin-top:1px;">{observacao}</div>'
                if observacao else ''
            )
            d += (
                f'<li onclick="abrirModalEvento({plantao.id}, \'{nome}\', \'{codigo}\', {horas}, \'{plantao.data}\')" '
                f'style="background-color: {cor}; color: white; padding: 3px 5px; border-radius: 3px; margin-bottom: 2px; '
                f'list-style: none; font-size: 0.85em; cursor: pointer;">'
                f'{nome} ({codigo}){obs_html}</li>'
            )
            
            # Contagem por especialidade do profissional
            esp = plantao.profissional.especialidade
            nome_esp = esp.nome if esp else 'Sem Especialidade'
            resumo_especialidade[nome_esp] = resumo_especialidade.get(nome_esp, 0) + 1

        resumo_html = ''
        if resumo_especialidade:
            resumo_html = '<div class="calendar-summary" style="margin-top: 5px; padding-top: 5px; border-top: 1px solid #eee; font-size: 0.8em;">'
            resumo_html += ' '.join([f'<span>{nome}: {qtd}</span><br />' for nome, qtd in resumo_especialidade.items()])
            resumo_html += '</div>'

        if day != 0:
            today = date.today()
            is_today = (today.year == self.year and today.month == self.month and today.day == day)
            td_class = "today" if is_today else ""
            return f"<td class='{td_class}'><span class='date'>{day}</span><ul>{d}</ul>{resumo_html}</td>"
        return '<td class="noday"></td>'

    def formatweek(self, theweek):
        s = ''.join(self.formatday(d, wd) for d, wd in theweek)
        return f'<tr>{s}</tr>'

    def formatmonth(self, withyear=True):
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week)}\n'
        return cal
