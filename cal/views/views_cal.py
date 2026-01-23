from datetime import datetime, timedelta, date
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
from django.db.models import Q
from ..models import EventoEscala, Matricula, TipoEvento
from core.models import Hospital, Setor
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
        
        user = self.request.user
        perfil = getattr(user, 'cal_perfil', None)
        plantoes = EventoEscala.objects.filter(data__range=[primeiro_dia, ultimo_dia])
        
        if not user.is_staff and perfil:
            if perfil.tipo == 'ESCALANTE':
                if hasattr(user, 'matricula') and user.matricula:
                    # Escalante vê tudo do seu setor, exceto o que foi criado por usuários 'ENFERMEIRO' (registros privados)
                    plantoes = plantoes.filter(
                        hospital=user.matricula.hospital, 
                        setor=user.matricula.setor
                    ).exclude(
                        criado_por__cal_perfil__tipo='ENFERMEIRO'
                    )
            elif perfil.tipo == 'ENFERMEIRO':
                if hasattr(user, 'matricula') and user.matricula:
                    # Enfermeiro vê o que ele mesmo criou (pessoal) E o que foi criado por ESCALANTE/ADMIN para o setor dele (oficial)
                    plantoes = plantoes.filter(
                        Q(profissional=user.matricula) | 
                        (Q(setor=user.matricula.setor) & (Q(criado_por__cal_perfil__tipo='ESCALANTE') | Q(criado_por__is_staff=True)))
                    )
        
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
        user = self.request.user
        perfil = getattr(user, 'cal_perfil', None)
        
        if user.is_staff:
            context['enfermeiros'] = Matricula.objects.filter(ativo=True)
        elif perfil and perfil.tipo == 'ESCALANTE' and hasattr(user, 'matricula'):
            context['enfermeiros'] = Matricula.objects.filter(
                hospital=user.matricula.hospital,
                setor=user.matricula.setor,
                ativo=True
            )
        elif perfil and perfil.tipo == 'ENFERMEIRO' and hasattr(user, 'matricula'):
            context['enfermeiros'] = Matricula.objects.filter(id=user.matricula.id)
        else:
            context['enfermeiros'] = Matricula.objects.none()
            
        context['tipos_plantao'] = TipoEvento.objects.all()
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
        
        user = request.user
        perfil = getattr(user, 'cal_perfil', None)
        if not user.is_staff:
            if not hasattr(user, 'matricula') or not user.matricula:
                messages.error(request, 'Seu usuário não possui uma matrícula vinculada.')
                return redirect('cal:event_new')
                
            if perfil.tipo == 'ENFERMEIRO' and enfermeiro.user != user:
                messages.error(request, 'Você só pode registrar plantões para si mesmo.')
                return redirect('cal:event_new')
            if perfil.tipo == 'ESCALANTE' and (enfermeiro.hospital != user.matricula.hospital or enfermeiro.setor != user.matricula.setor):
                messages.error(request, 'Você só pode escalar profissionais do seu hospital e setor.')
                return redirect('cal:event_new')

        for i in range(len(datas)):
            if not datas[i] or not tipos[i]: continue
            data_dt = datetime.strptime(datas[i], '%Y-%m-%d').date()
            tipo = get_object_or_404(TipoEvento, pk=tipos[i])
            EventoEscala.objects.create(
                profissional=enfermeiro,
                tipo=tipo,
                data=data_dt,
                setor=enfermeiro.setor,
                hospital=enfermeiro.hospital,
                observacao=obs[i] if i < len(obs) else '',
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

class MeusPlantoesListView(LoginRequiredMixin, ListView):
    model = EventoEscala
    template_name = 'cal/lista_eventos.html'
    context_object_name = 'eventos'
    
    def get_queryset(self):
        user = self.request.user
        perfil = getattr(user, 'cal_perfil', None)
        
        if user.is_superuser or user.is_staff:
            return EventoEscala.objects.all().order_by('data')
        
        if perfil and perfil.tipo == 'ESCALANTE' and hasattr(user, 'matricula'):
            return EventoEscala.objects.filter(
                hospital=user.matricula.hospital,
                setor=user.matricula.setor
            ).order_by('data')
            
        if perfil and perfil.tipo == 'ENFERMEIRO' and hasattr(user, 'matricula'):
            return EventoEscala.objects.filter(profissional=user.matricula).order_by('data')
            
        return EventoEscala.objects.filter(criado_por=user).order_by('data')

def excluir_evento(request, event_id):
    p = get_object_or_404(EventoEscala, pk=event_id)
    p.delete()
    return redirect('cal:listar_eventos')
