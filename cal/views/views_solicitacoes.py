# views_solicitacoes.py
from django.views.generic import CreateView, ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..models import Solicitacao, Plantao
from ..forms import SolicitacaoForm

class SolicitacaoCreateView(LoginRequiredMixin, CreateView):
    model = Solicitacao
    form_class = SolicitacaoForm
    template_name = 'solicitacoes/solicitacao_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.enfermeiro = self.request.user.perfil.enfermeiro
        form.instance.status = 'PENDENTE'

        # Validar datas para férias/folga
        if form.instance.tipo in ['FERIAS', 'FOLGA']:
            if form.instance.data_fim < form.instance.data_inicio:
                form.add_error('data_fim', 'Data final deve ser posterior à data inicial')
                return self.form_invalid(form)

        messages.success(self.request, 'Solicitação enviada para aprovação.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('minhas_solicitacoes')

class MinhasSolicitacoesListView(LoginRequiredMixin, ListView):
    model = Solicitacao
    template_name = 'solicitacoes/minhas_solicitacoes.html'
    context_object_name = 'solicitacoes'

    def get_queryset(self):
        return Solicitacao.objects.filter(
            enfermeiro=self.request.user.perfil.enfermeiro
        ).order_by('-data_solicitacao')

class SolicitacaoAprovarView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Solicitacao
    fields = ['status', 'justificativa_aprovacao']
    template_name = 'solicitacoes/aprovar_solicitacao.html'

    def test_func(self):
        return self.request.user.perfil.pode_aprovar

    def form_valid(self, form):
        if form.instance.status == 'APROVADA':
            form.instance.aprovado_por = self.request.user
            form.instance.data_aprovacao = timezone.now()

            # Processar aprovação baseado no tipo
            self._processar_aprovacao(form.instance)

            messages.success(self.request, 'Solicitação aprovada e processada.')
        elif form.instance.status == 'REJEITADA':
            messages.warning(self.request, 'Solicitação rejeitada.')

        return super().form_valid(form)

    def _processar_aprovacao(self, solicitacao):
        """Processa a solicitação aprovada"""
        if solicitacao.tipo == 'TROCA' and solicitacao.plantao_origem and solicitacao.enfermeiro_destino:
            # Realizar troca de plantão
            solicitacao.plantao_origem.enfermeiro = solicitacao.enfermeiro_destino
            solicitacao.plantao_origem.substituicao = True
            solicitacao.plantao_origem.substituido_por = solicitacao.enfermeiro
            solicitacao.plantao_origem.save()

        elif solicitacao.tipo == 'FOLGA':
            # Criar plantão de folga
            from .models import TipoPlantao, Plantao
            tipo_folga = TipoPlantao.objects.get(codigo='FOL')

            for single_date in self._daterange(solicitacao.data_inicio, solicitacao.data_fim):
                Plantao.objects.create(
                    enfermeiro=solicitacao.enfermeiro,
                    tipo_plantao=tipo_folga,
                    data=single_date,
                    setor=solicitacao.enfermeiro.setor_principal,
                    hospital=solicitacao.enfermeiro.hospitais.first()
                )

    def _daterange(self, start_date, end_date):
        from datetime import timedelta
        for n in range(int((end_date - start_date).days) + 1):
            yield start_date + timedelta(n)

    def get_success_url(self):
        return reverse_lazy('solicitacoes_pendentes')

class SolicitacoesPendentesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Solicitacao
    template_name = 'solicitacoes/solicitacoes_pendentes.html'
    context_object_name = 'solicitacoes'

    def test_func(self):
        return self.request.user.perfil.pode_aprovar

    def get_queryset(self):
        return Solicitacao.objects.filter(
            status='PENDENTE',
            plantao_origem__setor__in=self.request.user.perfil.enfermeiro.setores.all()
        ).order_by('data_solicitacao')