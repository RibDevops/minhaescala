from datetime import datetime, timedelta, date
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.utils.safestring import mark_safe
import calendar
from django.utils import timezone

from .models import *
from .utils import Calendar
from .forms import EventForm

from django.shortcuts import redirect


def index(request):
    return HttpResponse('hello')

class CalendarView(generic.ListView):
    model = Event
    template_name = 'cal/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        
        # Obter todos os eventos do mês
        events = Event.objects.filter(
            start_time__year=d.year,
            start_time__month=d.month
        )
        
        # Criar calendário com eventos
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True, events=events)
        
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['month_name'] = d.strftime("%B")  # Nome completo do mês
        context['year'] = d.year
        return context

def get_date(req_month):
    if req_month:
        year, month = (int(x) for x in req_month.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def event(request, event_id=None):
    instance = Event()
    if event_id:
        instance = get_object_or_404(Event, pk=event_id)
    else:
        instance = Event()

    form = EventForm(request.POST or None, instance=instance)
    if request.POST and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('cal:calendar'))
    return render(request, 'cal/event.html', {'form': form})

def listar_eventos(request):
    eventos = Event.objects.all().order_by('start_time')
    return render(request, 'cal/lista_eventos.html', {'eventos': eventos})




def excluir_evento(request, event_id):
    evento = get_object_or_404(Event, pk=event_id)
    evento.delete()
    return redirect('cal:listar_eventos')
