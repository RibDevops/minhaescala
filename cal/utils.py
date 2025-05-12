from asyncio import Event
import calendar
from datetime import datetime
import locale
from datetime import date

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')


class Calendar(calendar.HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    # def formatday(self, day, events):
    #     events_per_day = events.filter(start_time__day=day)
    #     d = ''
    #     for event in events_per_day:
    #         d += f'<li>{event.get_html_url}</li>'
        
    #     if day != 0:
    #         return f'<td><span class="date">{day}</span><ul>{d}</ul></td>'
    #     return '<td></td>'
   

    def formatday(self, day, events):
        events_per_day = events.filter(start_time__day=day)
        d = ''
        for event in events_per_day:
            d += f'<li>{event.get_html_url}</li>'
        
        if day != 0:
            css_class = 'today' if date(self.year, self.month, day) == datetime.today().date() else ''
            return f'<td class="{css_class}"><span class="date">{day}</span><ul>{d}</ul></td>'
        return '<td></td>'



    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f'<tr>{week}</tr>'
    
    def formatweekheader(self):
        dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        return '<tr>' + ''.join(f'<th class="header">{dia}</th>' for dia in dias_semana) + '</tr>'

    def formatmonthname(self, theyear, themonth, withyear=True):
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        nome_mes = meses[themonth - 1]
        if withyear:
            return f'<tr><th colspan="7" class="month">{nome_mes} {theyear}</th></tr>'
        return f'<tr><th colspan="7" class="month">{nome_mes}</th></tr>'
    
    def formatmonth(self, withyear=True, events=None):
        if events is None:
            events = Event.objects.none()
        
        cal = '<table class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        cal += '</table>'
        return cal
    
    

