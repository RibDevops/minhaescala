from calendar import HTMLCalendar
from .models import EventoEscala

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, plantoes=None):
        self.year = year
        self.month = month
        self.plantoes = plantoes
        super(Calendar, self).__init__()

    def formatday(self, day, weekday):
        plantoes_do_dia = self.plantoes.filter(data__day=day)
        d = ''
        resumo_especialidade = {}
        
        for plantao in plantoes_do_dia:
            nome = plantao.profissional.nome_exibicao
            codigo = plantao.tipo.codigo
            horas = plantao.tipo.horas
            d += f'<li>{nome} ({codigo} - {horas}h)</li>'
            
            # Contagem por especialidade do profissional
            esp = plantao.profissional.especialidade
            nome_esp = esp.nome if esp else 'Sem Especialidade'
            resumo_especialidade[nome_esp] = resumo_especialidade.get(nome_esp, 0) + 1

        resumo_html = ''
        if resumo_especialidade:
            resumo_html = '<div class="calendar-summary"><strong>QTD:</strong><br/>'
            resumo_html += ' '.join([f'<span>{nome}: {qtd}</span><br />' for nome, qtd in resumo_especialidade.items()])
            resumo_html += '</div>'

        if day != 0:
            return f"<td><span class='date'>{day}</span><ul>{d}</ul>{resumo_html}</td>"
        return '<td></td>'

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
