from django.urls import path, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from cal.models import Hospital, Setor, Matricula, Tipo, TipoEvento, Especialidade

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

# Tipo
class TipoListView(AdminRequiredMixin, ListView):
    model = Tipo
    template_name = 'cal/tipo/list.html'
    context_object_name = 'objetos'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Tipos', 'labels': ['Sigla', 'Descrição', 'Contabiliza'], 'create_url': 'cal:tipo_create', 'update_url': 'cal:tipo_update', 'delete_url': 'cal:tipo_delete'})
        return context

class TipoCreateView(AdminRequiredMixin, CreateView):
    model = Tipo
    fields = ['tipo', 'tipo_descricao', 'contabiliza']
    template_name = 'cal/tipo/form.html'
    success_url = reverse_lazy('cal:tipo_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Novo Tipo', 'cancel_url': reverse_lazy('cal:tipo_list')})
        return context

class TipoUpdateView(AdminRequiredMixin, UpdateView):
    model = Tipo
    fields = ['tipo', 'tipo_descricao', 'contabiliza']
    template_name = 'cal/tipo/form.html'
    success_url = reverse_lazy('cal:tipo_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': f'Editar Tipo: {self.object.tipo}', 'cancel_url': reverse_lazy('cal:tipo_list')})
        return context

class TipoDeleteView(AdminRequiredMixin, DeleteView):
    model = Tipo
    template_name = 'cal/tipo/confirm_delete.html'
    success_url = reverse_lazy('cal:tipo_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Excluir Tipo', 'cancel_url': reverse_lazy('cal:tipo_list')})
        return context

# TipoEvento
class TipoEventoListView(AdminRequiredMixin, ListView):
    model = TipoEvento
    template_name = 'cal/tipo_evento_list.html'
    context_object_name = 'objetos'
    def get_queryset(self):
        return TipoEvento.objects.all()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Tipos de Evento',
            'labels': ['Cor', 'Código', 'Descrição', 'Horas'],
            'create_url': 'cal:tipoevento_create',
            'update_url': 'cal:tipoevento_update',
            'delete_url': 'cal:tipoevento_delete'
        })
        return context

from cal.forms import (
    HospitalForm, SetorForm, MatriculaSimplificadaForm, 
    TipoEventoForm, TipoForm, EspecialidadeForm
)

class TipoEventoCreateView(AdminRequiredMixin, CreateView):
    model = TipoEvento
    form_class = TipoEventoForm
    template_name = 'cal/tipo_evento/form.html'
    success_url = reverse_lazy('cal:tipoevento_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Novo Tipo de Evento', 'cancel_url': reverse_lazy('cal:tipoevento_list')})
        return context

class TipoEventoUpdateView(AdminRequiredMixin, UpdateView):
    model = TipoEvento
    form_class = TipoEventoForm
    template_name = 'cal/tipo_evento/form.html'
    success_url = reverse_lazy('cal:tipoevento_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': f'Editar Tipo de Evento: {self.object.codigo}', 'cancel_url': reverse_lazy('cal:tipoevento_list')})
        return context

class TipoEventoDeleteView(AdminRequiredMixin, DeleteView):
    model = TipoEvento
    template_name = 'cal/tipo_evento/confirm_delete.html'
    success_url = reverse_lazy('cal:tipoevento_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Excluir Tipo de Evento', 'cancel_url': reverse_lazy('cal:tipoevento_list')})
        return context

# Hospital
class HospitalListView(AdminRequiredMixin, ListView):
    model = Hospital
    template_name = 'cal/hospital_list.html'
    context_object_name = 'objetos'
    def get_queryset(self):
        return Hospital.objects.all()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Hospitais', 'labels': ['Nome', 'Sigla'], 'create_url': 'cal:hospital_create', 'update_url': 'cal:hospital_update', 'delete_url': 'cal:hospital_delete'})
        return context

class HospitalCreateView(AdminRequiredMixin, CreateView):
    model = Hospital
    fields = ['nome', 'sigla']
    template_name = 'cal/hospital/form.html'
    success_url = reverse_lazy('cal:hospital_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Novo Hospital', 'cancel_url': reverse_lazy('cal:hospital_list')})
        return context

class HospitalUpdateView(AdminRequiredMixin, UpdateView):
    model = Hospital
    fields = ['nome', 'sigla']
    template_name = 'cal/hospital/form.html'
    success_url = reverse_lazy('cal:hospital_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': f'Editar Hospital: {self.object.nome}', 'cancel_url': reverse_lazy('cal:hospital_list')})
        return context

class HospitalDeleteView(AdminRequiredMixin, DeleteView):
    model = Hospital
    template_name = 'cal/hospital/confirm_delete.html'
    success_url = reverse_lazy('cal:hospital_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Excluir Hospital', 'cancel_url': reverse_lazy('cal:hospital_list')})
        return context

# Setor
class SetorListView(AdminRequiredMixin, ListView):
    model = Setor
    template_name = 'cal/setor_list.html'
    context_object_name = 'objetos'
    def get_queryset(self):
        return Setor.objects.all()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Setores', 'labels': ['Nome', 'Hospital'], 'create_url': 'cal:setor_create', 'update_url': 'cal:setor_update', 'delete_url': 'cal:setor_delete'})
        return context

class SetorCreateView(AdminRequiredMixin, CreateView):
    model = Setor
    fields = ['nome', 'hospital']
    template_name = 'cal/setor/form.html'
    success_url = reverse_lazy('cal:setor_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Novo Setor', 'cancel_url': reverse_lazy('cal:setor_list')})
        return context

class SetorUpdateView(AdminRequiredMixin, UpdateView):
    model = Setor
    fields = ['nome', 'hospital']
    template_name = 'cal/setor/form.html'
    success_url = reverse_lazy('cal:setor_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': f'Editar Setor: {self.object.nome}', 'cancel_url': reverse_lazy('cal:setor_list')})
        return context

class SetorDeleteView(AdminRequiredMixin, DeleteView):
    model = Setor
    template_name = 'cal/setor/confirm_delete.html'
    success_url = reverse_lazy('cal:setor_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Excluir Setor', 'cancel_url': reverse_lazy('cal:setor_list')})
        return context

# Especialidade
class EspecialidadeListView(AdminRequiredMixin, ListView):
    model = Especialidade
    template_name = 'cal/especialidade_list.html'
    context_object_name = 'objetos'
    def get_queryset(self):
        return Especialidade.objects.all()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Especialidades', 'labels': ['Nome'], 'create_url': 'cal:especialidade_create', 'update_url': 'cal:especialidade_update', 'delete_url': 'cal:especialidade_delete'})
        return context

class EspecialidadeCreateView(AdminRequiredMixin, CreateView):
    model = Especialidade
    fields = ['nome']
    template_name = 'cal/crud_base_form.html'
    success_url = reverse_lazy('cal:especialidade_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Nova Especialidade', 'cancel_url': reverse_lazy('cal:especialidade_list')})
        return context

class EspecialidadeUpdateView(AdminRequiredMixin, UpdateView):
    model = Especialidade
    fields = ['nome']
    template_name = 'cal/crud_base_form.html'
    success_url = reverse_lazy('cal:especialidade_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': f'Editar Especialidade: {self.object.nome}', 'cancel_url': reverse_lazy('cal:especialidade_list')})
        return context

class EspecialidadeDeleteView(AdminRequiredMixin, DeleteView):
    model = Especialidade
    template_name = 'cal/crud_base_confirm_delete.html'
    success_url = reverse_lazy('cal:especialidade_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Excluir Especialidade', 'cancel_url': reverse_lazy('cal:especialidade_list')})
        return context

# Matricula
class MatriculaListView(AdminRequiredMixin, ListView):
    model = Matricula
    template_name = 'cal/matricula/list.html'
    context_object_name = 'objetos'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Matrículas', 'labels': ['Matrícula', 'Nome Guerra', 'Carga Horária'], 'create_url': 'cal:matricula_create', 'update_url': 'cal:matricula_update', 'delete_url': 'cal:matricula_delete'})
        return context

class MatriculaCreateView(AdminRequiredMixin, CreateView):
    model = Matricula
    fields = ['matricula', 'nome_completo', 'nome_guerra', 'coren', 'hospital', 'setor', 'carga_horaria_semanal', 'ativo']
    template_name = 'cal/matricula/form.html'
    success_url = reverse_lazy('cal:matricula_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Nova Matrícula', 'cancel_url': reverse_lazy('cal:matricula_list')})
        return context

class MatriculaUpdateView(AdminRequiredMixin, UpdateView):
    model = Matricula
    fields = ['matricula', 'nome_completo', 'nome_guerra', 'coren', 'hospital', 'setor', 'carga_horaria_semanal', 'ativo']
    template_name = 'cal/matricula/form.html'
    success_url = reverse_lazy('cal:matricula_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': f'Editar Matrícula: {self.object.matricula}', 'cancel_url': reverse_lazy('cal:matricula_list')})
        return context

class MatriculaDeleteView(AdminRequiredMixin, DeleteView):
    model = Matricula
    template_name = 'cal/matricula/confirm_delete.html'
    success_url = reverse_lazy('cal:matricula_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Excluir Matrícula', 'cancel_url': reverse_lazy('cal:matricula_list')})
        return context
