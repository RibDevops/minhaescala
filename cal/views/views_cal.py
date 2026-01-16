from datetime import datetime, timedelta, date
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
from ..models import Plantao, Enfermeiro, Escala
from ..forms import PlantaoForm
from ..utils import Calendar

class CalendarioView(LoginRequiredMixin, TemplateView):
    template_name = 'cal/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.request.GET.get('month')
        if month:
            try:
                d = datetime.strptime(month, "%Y-%m").date()
            except ValueError:
                d = datetime.today().date().replace(day=1)
        else:
            d = datetime.today().date().replace(day=1)
        
        primeiro_dia = d.replace(day=1)
        if primeiro_dia.month == 12:
            ultimo_dia = primeiro_dia.replace(year=primeiro_dia.year+1, month=1, day=1) - timedelta(days=1)
        else:
            ultimo_dia = primeiro_dia.replace(month=primeiro_dia.month+1, day=1) - timedelta(days=1)
        
        plantoes = Plantao.objects.filter(data__range=[primeiro_dia, ultimo_dia])
        # Removida a restrição de visualização para profissionais
        # Qualquer usuário logado pode ver todos os plantões no calendário
        
        cal = Calendar(d.year, d.month, plantoes)
        html_cal = cal.formatmonth(withyear=True)
        
        context.update({
            'primeiro_dia': primeiro_dia,
            'ultimo_dia': ultimo_dia,
            'calendar': mark_safe(html_cal),
            'mes_atual': d.strftime("%Y-%m"),
            'mes_anterior': (primeiro_dia - timedelta(days=1)).strftime("%Y-%m"),
            'mes_seguinte': (ultimo_dia + timedelta(days=1)).strftime("%Y-%m"),
        })
        return context

class PlantaoCreateView(LoginRequiredMixin, CreateView):
    model = Plantao
    form_class = PlantaoForm
    template_name = 'cal/event.html'
    success_url = reverse_lazy('cal:calendar')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        escala, _ = Escala.objects.get_or_create(
            mes_referencia=form.cleaned_data['data'].replace(day=1),
            setor=form.cleaned_data['setor'],
            defaults={'criado_por': self.request.user}
        )
        form.instance.escala = escala
        messages.success(self.request, 'Plantão criado!')
        return super().form_valid(form)

class PlantaoUpdateView(LoginRequiredMixin, UpdateView):
    model = Plantao
    form_class = PlantaoForm
    template_name = 'cal/event.html'
    success_url = reverse_lazy('cal:calendar')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class PlantaoDeleteView(LoginRequiredMixin, DeleteView):
    model = Plantao
    success_url = reverse_lazy('cal:calendar')

class MeusPlantoesListView(LoginRequiredMixin, ListView):
    model = Plantao
    template_name = 'cal/lista_eventos.html'
    context_object_name = 'eventos'
    def get_queryset(self):
        if hasattr(self.request.user, 'perfil') and hasattr(self.request.user.perfil, 'enfermeiro'):
            return Plantao.objects.filter(enfermeiro=self.request.user.perfil.enfermeiro, data__gte=date.today()).order_by('data')
        return Plantao.objects.none()

def excluir_evento(request, event_id):
    p = get_object_or_404(Plantao, pk=event_id)
    p.delete()
    return redirect('cal:listar_eventos')
