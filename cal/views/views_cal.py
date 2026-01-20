from datetime import datetime, timedelta, date
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
from ..models import EventoEscala, Matricula, TipoEvento, Hospital, Setor
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
        
        plantoes = EventoEscala.objects.filter(data__range=[primeiro_dia, ultimo_dia])
        
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

class PlantaoCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'cal/event.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from ..models import Matricula, TipoEvento, Hospital, Setor
        
        user = self.request.user
        if user.is_staff:
            context['enfermeiros'] = Matricula.objects.all()
        elif hasattr(user, 'perfil') and user.perfil.matriculas.exists():
            # Pegamos o hospital e setor da primeira matrícula do perfil logado
            primeira_matricula = user.perfil.matriculas.first()
            context['enfermeiros'] = Matricula.objects.filter(
                hospital=primeira_matricula.hospital,
                setor=primeira_matricula.setor
            )
        else:
            context['enfermeiros'] = Matricula.objects.none()
            
        context['tipos_plantao'] = TipoEvento.objects.all()
        # Adicionando formulário para compatibilidade
        from ..forms import PlantaoForm
        context['form'] = PlantaoForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        enfermeiro_id = request.POST.get('enfermeiro')
        datas = request.POST.getlist('data[]')
        tipos = request.POST.getlist('tipo_plantao[]')
        obs = request.POST.getlist('observacoes[]')

        if not enfermeiro_id or not datas:
            messages.error(request, 'Dados inválidos')
            return redirect('cal:event_new')

        enfermeiro = get_object_or_404(Matricula, pk=enfermeiro_id)
        
        # Como agora a matrícula tem hospital e setor fixos, usamos os dela
        if not enfermeiro.hospital or not enfermeiro.setor:
            messages.error(request, f'O profissional {enfermeiro.nome_exibicao} não possui hospital ou setor vinculado.')
            return redirect('cal:event_new')

        for i in range(len(datas)):
            if not datas[i] or not tipos[i]: continue
            
            data_dt = datetime.strptime(datas[i], '%Y-%m-%d').date()
            tipo = get_object_or_404(TipoEvento, pk=tipos[i])
            
            # Use color from form if provided, otherwise default to tipo_evento color
            cor_evento = request.POST.get('cor', tipo.cor)

            EventoEscala.objects.create(
                profissional=enfermeiro,
                tipo_evento=tipo,
                data=data_dt,
                setor=enfermeiro.setor,
                hospital=enfermeiro.hospital,
                cor=cor_evento,
                observacoes=obs[i] if i < len(obs) else '',
                criado_por=request.user
            )
            
        messages.success(request, f'Plantões registrados para {enfermeiro.nome_exibicao}')
        return redirect('cal:calendar')

class PlantaoUpdateView(LoginRequiredMixin, UpdateView):
    model = EventoEscala
    form_class = PlantaoForm
    template_name = 'cal/event.html'
    success_url = reverse_lazy('cal:calendar')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class PlantaoDeleteView(LoginRequiredMixin, DeleteView):
    model = EventoEscala
    success_url = reverse_lazy('cal:calendar')

from django.db.models import Q

class MeusPlantoesListView(LoginRequiredMixin, ListView):
    model = EventoEscala
    template_name = 'cal/lista_eventos.html'
    context_object_name = 'eventos'
    
    def get_queryset(self):
        user = self.request.user
        
        # 1. ADMIN: Vê absolutamente tudo
        if user.is_superuser or (hasattr(user, 'perfil') and user.perfil.tipo_usuario == 'ADMIN'):
            return EventoEscala.objects.all().order_by('data')
        
        if not hasattr(user, 'perfil'):
            return EventoEscala.objects.none()
            
        perfil = user.perfil
        
        # 2. ESCALANTE: Vê o setor dele, mas não vê registros privados de enfermeiros
        if perfil.tipo_usuario == 'ESCALANTE':
            matricula = perfil.matriculas.first() 
            if not matricula:
                return EventoEscala.objects.none()
            return EventoEscala.objects.filter(
                hospital=matricula.hospital,
                setor=matricula.setor
            ).exclude(
                criado_por__perfil__tipo_usuario='PROFISSIONAL'
            ).order_by('data')
        
        # 3. PROFISSIONAL (Enfermeiro): Vê a escala oficial (Escalante) + Seus próprios registros
        else:
            matricula = perfil.matriculas.first()
            if not matricula:
                return EventoEscala.objects.filter(criado_por=user).order_by('data')
            return EventoEscala.objects.filter(
                Q(criado_por=user) | # Seus próprios registros
                (Q(setor=matricula.setor) & Q(criado_por__perfil__tipo_usuario='ESCALANTE')) # Escala oficial
            ).order_by('data')

def excluir_evento(request, event_id):
    p = get_object_or_404(EventoEscala, pk=event_id)
    p.delete()
    return redirect('cal:listar_eventos')
