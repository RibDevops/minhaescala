from calendar import HTMLCalendar
from .models import Plantao

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, plantoes=None):
        self.year = year
        self.month = month
        self.plantoes = plantoes
        super(Calendar, self).__init__()

    def formatday(self, day, weekday):
        plantoes_do_dia = self.plantoes.filter(data__day=day)
        d = ''
        for plantao in plantoes_do_dia:
            # Prioriza o campo 'nome', depois 'nome_completo'
            nome_exibicao = plantao.enfermeiro.nome or plantao.enfermeiro.nome_completo
            # Adicionando o código do plantão e as horas
            d += f'<li>{nome_exibicao} ({plantao.tipo_plantao.codigo} - {plantao.tipo_plantao.horas}h)</li>'

        if day != 0:
            return f"<td><span class='date'>{day}</span><ul>{d}</ul></td>"
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
