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
        s = f'{nome_mes} {theyear}' if withyear else nome_mes
        return f'<tr><th colspan="7" class="month">{s}</th></tr>'

    def formatweekheader(self):
        s = ''.join(f'<th class="{self.cssclasses[i]}">{DIAS_SEMANA_PT[i]}</th>' for i in range(7))
        return f'<tr>{s}</tr>'

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday"></td>'

        plantoes_do_dia = self.plantoes.filter(data__day=day)
        d = ''
        resumo_especialidade = {}

        for plantao in plantoes_do_dia:
            nome = plantao.profissional.nome_exibicao
            codigo = plantao.tipo.codigo if plantao.tipo else '—'
            horas = plantao.tipo.horas or 0 if plantao.tipo else 0
            cor = plantao.tipo.cor if plantao.tipo else '#999'
            observacao = plantao.observacao or ''

            # Escapar para atributos HTML (evita quebra com apóstrofes/aspas nos nomes)
            nome_esc = nome.replace('&', '&amp;').replace('"', '&quot;')
            obs_esc = observacao.replace('&', '&amp;').replace('"', '&quot;')

            obs_html = (
                f'<div class="evento-obs">{observacao}</div>'
                if observacao else ''
            )

            d += (
                f'<li class="evento-item" '
                f'data-id="{plantao.id}" '
                f'data-nome="{nome_esc}" '
                f'data-codigo="{codigo}" '
                f'data-horas="{horas}" '
                f'data-data="{plantao.data}" '
                f'data-obs="{obs_esc}" '
                f'style="background-color:{cor};">'
                f'<span class="evento-nome">{nome}</span>'
                f'<span class="evento-paren"> (</span>'
                f'<span class="evento-codigo">{codigo}</span>'
                f'<span class="evento-paren">)</span>'
                f'{obs_html}'
                f'</li>'
            )

            esp = plantao.profissional.especialidade
            nome_esp = esp.nome if esp else 'Sem Especialidade'
            resumo_especialidade[nome_esp] = resumo_especialidade.get(nome_esp, 0) + 1

        resumo_html = ''
        if resumo_especialidade:
            resumo_html = '<div class="calendar-summary">'
            resumo_html += ' '.join(
                [f'<span>{n}: {q}</span><br>' for n, q in resumo_especialidade.items()]
            )
            resumo_html += '</div>'

        today = date.today()
        is_today = (today.year == self.year and today.month == self.month and today.day == day)
        td_class = "today" if is_today else ""

        return (
            f"<td class='{td_class}'>"
            f"<span class='date'>{day}</span>"
            f"<ul>{d}</ul>"
            f"{resumo_html}"
            f"</td>"
        )

    def formatweek(self, theweek):
        s = ''.join(self.formatday(d, wd) for d, wd in theweek)
        return f'<tr>{s}</tr>'

    def formatmonth(self, withyear=True):
        cal = '<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week)}\n'
        return cal
