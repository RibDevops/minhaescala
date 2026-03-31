from datetime import datetime, timedelta, date
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.safestring import mark_safe
from django.db.models import Q
from ..models import EventoEscala, Matricula, TipoEvento
from core.models import Hospital, Setor
from ..forms import PlantaoForm
from ..utils import Calendar
from ..permissions import (
    get_perfil, get_matricula,
    is_admin, is_escalante, is_enfermeiro, is_escalante_ou_admin,
)


def is_enfermeiro_criador(evento):
    """True se o evento foi criado por um usuário com papel ENFERMEIRO."""
    perfil = get_perfil(evento.criado_por) if evento.criado_por else None
    return perfil is not None and perfil.tipo == 'ENFERMEIRO'

from django.template.defaulttags import register

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary[key]
    except (IndexError, KeyError, TypeError):
        return ""

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
        plantoes = EventoEscala.objects.filter(
            data__range=[primeiro_dia, ultimo_dia]
        ).select_related('tipo', 'profissional', 'hospital', 'setor', 'criado_por')
        
        matricula = get_matricula(user)
        pode_editar = True  # por padrão, usuários autenticados podem editar

        if not user.is_staff and perfil:
            if perfil.tipo == 'ESCALANTE':
                if matricula:
                    # Escalante vê TODA a escala do setor (inclui seus próprios plantões)
                    # Exclui apenas registros PRIVADOS de outros enfermeiros (criados por eles mesmos para si)
                    plantoes = plantoes.filter(
                        hospital=matricula.hospital,
                        setor=matricula.setor
                    ).exclude(
                        # Exclui registros criados por ENFERMEIRO para si mesmo (privados)
                        # Mas não exclui os criados pelo escalante para si mesmo
                        Q(criado_por__cal_perfil__tipo='ENFERMEIRO') & ~Q(criado_por=user)
                    )
            elif perfil.tipo == 'ENFERMEIRO':
                if matricula:
                    # Enfermeiro vê a escala COMPLETA do setor (somente leitura)
                    # Vê plantões oficiais do setor + seus próprios registros privados
                    plantoes = plantoes.filter(
                        Q(setor=matricula.setor, hospital=matricula.hospital) &
                        ~Q(criado_por__cal_perfil__tipo='ENFERMEIRO') |
                        Q(profissional=matricula)
                    ).distinct()
                    pode_editar = False  # Enfermeiro não edita

        cal = Calendar(d.year, d.month, plantoes)
        html_cal = cal.formatmonth(withyear=True)

        from ..utils import MESES_PT
        mes_nome = f"{MESES_PT[d.month]} {d.year}"

        context.update({
            'primeiro_dia': primeiro_dia,
            'ultimo_dia': ultimo_dia,
            'calendar': mark_safe(html_cal),
            'mes_atual': d.strftime("%Y-%m"),
            'mes_anterior': (primeiro_dia - timedelta(days=1)).strftime("%Y-%m"),
            'mes_seguinte': (ultimo_dia + timedelta(days=1)).strftime("%Y-%m"),
            'pode_editar': pode_editar,
            'mes_nome': mes_nome,
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
        forcar_carga = request.POST.get('forcar_carga') == '1'

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
            if not datas[i] or not tipos[i]:
                continue
            data_dt = datetime.strptime(datas[i], '%Y-%m-%d').date()
            tipo = get_object_or_404(TipoEvento, pk=tipos[i])
            evento = EventoEscala(
                profissional=enfermeiro,
                tipo=tipo,
                data=data_dt,
                setor=enfermeiro.setor,
                hospital=enfermeiro.hospital,
                observacao=obs[i] if i < len(obs) else '',
                criado_por=request.user,
            )
            evento.save(forcar_carga=forcar_carga)

        messages.success(request, f'Plantões registrados para {enfermeiro.nome_exibicao}')
        return redirect('cal:calendar')

class PlantaoUpdateView(LoginRequiredMixin, UpdateView):
    model = EventoEscala
    form_class = PlantaoForm
    template_name = 'cal/event.html'
    success_url = reverse_lazy('cal:calendar')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if is_admin(user):
            return obj
        matricula = get_matricula(user)
        if is_escalante(user) and matricula:
            if obj.hospital == matricula.hospital and obj.setor == matricula.setor and not is_enfermeiro_criador(obj):
                return obj
        if is_enfermeiro(user):
            if obj.criado_por == user and obj.profissional == matricula:
                return obj
        raise PermissionDenied

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

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
        context['is_edit'] = True
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        enfermeiro_id = request.POST.get('enfermeiro')
        datas = request.POST.getlist('data[]')
        tipos = request.POST.getlist('tipo_plantao[]')
        obs = request.POST.getlist('observacoes[]')
        forcar_carga = request.POST.get('forcar_carga') == '1'
        next_url = request.POST.get('next', '')

        if not enfermeiro_id or not datas:
            messages.error(request, 'Dados inválidos')
            return self.get(request, *args, **kwargs)

        enfermeiro = get_object_or_404(Matricula, pk=enfermeiro_id)
        data_dt = datetime.strptime(datas[0], '%Y-%m-%d').date()
        tipo = get_object_or_404(TipoEvento, pk=tipos[0])

        self.object.profissional = enfermeiro
        self.object.data = data_dt
        self.object.tipo = tipo
        self.object.observacao = obs[0] if obs else ''
        self.object.hospital = enfermeiro.hospital
        self.object.setor = enfermeiro.setor
        self.object.save(forcar_carga=forcar_carga)

        messages.success(request, f'Plantão de {enfermeiro.nome_exibicao} atualizado com sucesso.')
        return redirect(next_url if next_url else self.success_url)

class PlantaoDeleteView(LoginRequiredMixin, DeleteView):
    model = EventoEscala
    template_name = 'cal/plantao_confirm_delete.html'

    def get_success_url(self):
        next_url = self.request.POST.get('next', '') or self.request.GET.get('next', '')
        return next_url if next_url else reverse_lazy('cal:calendar')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if is_admin(user):
            return obj
        matricula = get_matricula(user)
        if is_escalante(user) and matricula:
            # Escalante só deleta plantões oficiais do seu setor
            if obj.hospital == matricula.hospital and obj.setor == matricula.setor and not is_enfermeiro_criador(obj):
                return obj
        if is_enfermeiro(user):
            # Enfermeiro só deleta os seus próprios registros privados
            if obj.criado_por == user and obj.profissional == matricula:
                return obj
        raise PermissionDenied

class MeusPlantoesListView(LoginRequiredMixin, ListView):
    model = EventoEscala
    template_name = 'cal/lista_eventos.html'
    context_object_name = 'eventos'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pode_editar'] = not is_enfermeiro(self.request.user)
        return context

    def get_queryset(self):
        user = self.request.user
        matricula = get_matricula(user)

        base_qs = EventoEscala.objects.select_related(
            'tipo', 'profissional', 'hospital', 'setor', 'criado_por'
        )

        if is_admin(user):
            return base_qs.all().order_by('data')

        if not matricula:
            return EventoEscala.objects.none()

        if is_escalante(user):
            # Escalante vê toda a escala do setor, exceto registros privados de outros enfermeiros
            return base_qs.filter(
                hospital=matricula.hospital,
                setor=matricula.setor,
            ).exclude(
                Q(criado_por__cal_perfil__tipo='ENFERMEIRO') & ~Q(criado_por=user)
            ).order_by('data')

        if is_enfermeiro(user):
            # Enfermeiro vê toda a escala oficial do setor + seus próprios registros
            oficiais = Q(
                hospital=matricula.hospital,
                setor=matricula.setor,
            ) & ~Q(criado_por__cal_perfil__tipo='ENFERMEIRO')
            privados = Q(profissional=matricula)
            return base_qs.filter(oficiais | privados).distinct().order_by('data')

        return EventoEscala.objects.none()

@login_required
def excluir_evento(request, event_id):
    evento = get_object_or_404(EventoEscala, pk=event_id)
    user = request.user
    matricula = get_matricula(user)

    if is_admin(user):
        pass  # acesso total
    elif is_escalante(user) and matricula:
        if not (evento.hospital == matricula.hospital and evento.setor == matricula.setor and not is_enfermeiro_criador(evento)):
            raise PermissionDenied
    elif is_enfermeiro(user):
        if not (evento.criado_por == user and evento.profissional == matricula):
            raise PermissionDenied
    else:
        raise PermissionDenied

    evento.delete()
    return redirect('cal:listar_eventos')

@login_required
def plantoes_por_profissional(request):
    """Lista todos os plantões agrupados por profissional."""
    from ..models import Matricula
    user = request.user
    matricula_usuario = get_matricula(user)

    if is_admin(user):
        profissionais = Matricula.objects.filter(ativo=True).order_by('nome_completo')
    elif matricula_usuario:
        profissionais = Matricula.objects.filter(
            hospital=matricula_usuario.hospital,
            setor=matricula_usuario.setor,
            ativo=True
        ).order_by('nome_completo')
    else:
        profissionais = Matricula.objects.none()

    # Filtros de mês/ano
    from datetime import datetime
    hoje = datetime.today()
    mes = int(request.GET.get('mes', hoje.month))
    ano = int(request.GET.get('ano', hoje.year))

    from datetime import date
    from calendar import monthrange
    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])

    dados = []
    for prof in profissionais:
        eventos = EventoEscala.objects.filter(
            profissional=prof,
            data__range=[primeiro_dia, ultimo_dia]
        ).select_related('tipo').order_by('data')
        if eventos.exists():
            dados.append({
                'profissional': prof,
                'eventos': eventos,
                'total_horas': sum(e.tipo.horas for e in eventos if e.tipo),
                'total_plantoes': eventos.count(),
            })

    meses = [
        (1,'Janeiro'),(2,'Fevereiro'),(3,'Março'),(4,'Abril'),
        (5,'Maio'),(6,'Junho'),(7,'Julho'),(8,'Agosto'),
        (9,'Setembro'),(10,'Outubro'),(11,'Novembro'),(12,'Dezembro'),
    ]

    tipos_plantao = TipoEvento.objects.all()

    # Paginação: 10 profissionais por página
    from django.core.paginator import Paginator
    paginator = Paginator(dados, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'cal/plantoes_por_profissional.html', {
        'dados': page_obj,
        'page_obj': page_obj,
        'mes': mes,
        'tipos_plantao': tipos_plantao,
        'ano': ano,
        'meses': meses,
    })


from django.http import JsonResponse

@login_required
def validar_carga_horaria(request):
    enfermeiro_id = request.GET.get('enfermeiro')
    data_str = request.GET.get('data')
    tipo_id = request.GET.get('tipo')

    if not all([enfermeiro_id, data_str, tipo_id]):
        return JsonResponse({'error': 'Parâmetros ausentes'}, status=400)

    try:
        from ..utils_saldo import inicio_semana, fim_semana
        enfermeiro = Matricula.objects.get(pk=enfermeiro_id)
        data_dt = datetime.strptime(data_str, '%Y-%m-%d').date()
        tipo = TipoEvento.objects.get(pk=tipo_id)

        # Usa a semana real dom–sáb que contém a data informada
        inicio = inicio_semana(data_dt)
        fim = fim_semana(data_dt)

        eventos = EventoEscala.objects.filter(
            profissional=enfermeiro,
            data__range=(inicio, fim),
            tipo__tipo_base__contabiliza=True,
        )
        carga_atual = sum(e.tipo.horas for e in eventos)
        total = carga_atual + (tipo.horas or 0)
        limite = enfermeiro.carga_horaria_semanal or 0
        excedeu = limite > 0 and total > limite

        return JsonResponse({
            'total': total,
            'limite': limite,
            'excedeu': excedeu,
            'semana_inicio': inicio.strftime('%d/%m'),
            'semana_fim': fim.strftime('%d/%m'),
            'mensagem': (
                f"Carga da semana ({inicio.strftime('%d/%m')}–{fim.strftime('%d/%m')}) "
                f"atingirá {total}h — limite: {limite}h"
            ) if excedeu else ''
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
