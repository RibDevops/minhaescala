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
        resumo = {}
        
        for plantao in plantoes_do_dia:
            nome_exibicao = plantao.profissional.nome_exibicao
            codigo = plantao.tipo_evento.codigo
            horas = plantao.tipo_evento.horas
            d += f'<li>{nome_exibicao} ({codigo} - {horas}h)</li>'
            
            chave_resumo = plantao.tipo_evento.codigo
            resumo[chave_resumo] = resumo.get(chave_resumo, 0) + 1

        resumo_html = ''
        if resumo:
            resumo_html = '<div class="calendar-summary"><strong>QTD ESP:</strong><br/>'
            resumo_html += ' '.join([f'<span>{nome}: {qtd}</span><br />' for nome, qtd in resumo.items()])
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
