from django.urls import path, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from cal.models import Matricula, TipoEvento
from cal.forms import TipoEventoForm
from core.models import Hospital, Setor

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

# Hospital
class HospitalListView(AdminRequiredMixin, ListView):
    model = Hospital
    template_name = 'cal/hospital_list.html'
    context_object_name = 'objetos'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Hospitais', 'labels': ['Nome', 'Sigla'], 'create_url': 'cal:hospital_create', 'update_url': 'cal:hospital_update', 'delete_url': 'cal:hospital_delete'})
        return context

class HospitalCreateView(AdminRequiredMixin, CreateView):
    model = Hospital
    fields = ['nome', 'sigla']
    template_name = 'cal/crud_base_form.html'
    success_url = reverse_lazy('cal:hospital_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Novo Hospital', 'cancel_url': reverse_lazy('cal:hospital_list')})
        return context

class HospitalUpdateView(AdminRequiredMixin, UpdateView):
    model = Hospital
    fields = ['nome', 'sigla']
    template_name = 'cal/crud_base_form.html'
    success_url = reverse_lazy('cal:hospital_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': f'Editar Hospital: {self.object.nome}', 'cancel_url': reverse_lazy('cal:hospital_list')})
        return context

class HospitalDeleteView(AdminRequiredMixin, DeleteView):
    model = Hospital
    template_name = 'cal/crud_base_confirm_delete.html'
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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Setores', 'labels': ['Nome', 'Hospital'], 'create_url': 'cal:setor_create', 'update_url': 'cal:setor_update', 'delete_url': 'cal:setor_delete'})
        return context

class SetorCreateView(AdminRequiredMixin, CreateView):
    model = Setor
    fields = ['nome', 'hospital']
    template_name = 'cal/crud_base_form.html'
    success_url = reverse_lazy('cal:setor_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Novo Setor', 'cancel_url': reverse_lazy('cal:setor_list')})
        return context

class SetorUpdateView(AdminRequiredMixin, UpdateView):
    model = Setor
    fields = ['nome', 'hospital']
    template_name = 'cal/crud_base_form.html'
    success_url = reverse_lazy('cal:setor_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': f'Editar Setor: {self.object.nome}', 'cancel_url': reverse_lazy('cal:setor_list')})
        return context

class SetorDeleteView(AdminRequiredMixin, DeleteView):
    model = Setor
    template_name = 'cal/crud_base_confirm_delete.html'
    success_url = reverse_lazy('cal:setor_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Excluir Setor', 'cancel_url': reverse_lazy('cal:setor_list')})
        return context

# Matricula
class MatriculaListView(AdminRequiredMixin, ListView):
    model = Matricula
    template_name = 'cal/matricula_list.html'
    context_object_name = 'objetos'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Matrículas', 'labels': ['Matrícula', 'Nome Guerra', 'Carga Horária'], 'create_url': 'cal:matricula_create', 'update_url': 'cal:matricula_update', 'delete_url': 'cal:matricula_delete'})
        return context

class MatriculaCreateView(AdminRequiredMixin, CreateView):
    model = Matricula
    fields = ['matricula', 'nome_completo', 'nome_guerra', 'coren', 'hospital', 'setor', 'carga_horaria_semanal', 'ativo']
    template_name = 'cal/crud_base_form.html'
    success_url = reverse_lazy('cal:matricula_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Nova Matrícula', 'cancel_url': reverse_lazy('cal:matricula_list')})
        return context

class MatriculaUpdateView(AdminRequiredMixin, UpdateView):
    model = Matricula
    fields = ['matricula', 'nome_completo', 'nome_guerra', 'coren', 'hospital', 'setor', 'carga_horaria_semanal', 'ativo']
    template_name = 'cal/crud_base_form.html'
    success_url = reverse_lazy('cal:matricula_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': f'Editar Matrícula: {self.object.matricula}', 'cancel_url': reverse_lazy('cal:matricula_list')})
        return context

class MatriculaDeleteView(AdminRequiredMixin, DeleteView):
    model = Matricula
    template_name = 'cal/crud_base_confirm_delete.html'
    success_url = reverse_lazy('cal:matricula_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Excluir Matrícula', 'cancel_url': reverse_lazy('cal:matricula_list')})
        return context

# TipoEvento
class TipoEventoListView(AdminRequiredMixin, ListView):
    model = TipoEvento
    template_name = 'cal/tipo_evento_list.html'
    context_object_name = 'objetos'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Tipos de Evento',
            'labels': ['Cor', 'Código', 'Descrição', 'Horas'],
            'create_url': 'cal:tipo_evento_create',
            'update_url': 'cal:tipo_evento_update',
            'delete_url': 'cal:tipo_evento_delete'
        })
        return context

class TipoEventoCreateView(AdminRequiredMixin, CreateView):
    model = TipoEvento
    form_class = TipoEventoForm
    template_name = 'cal/crud_base_form.html'
    success_url = reverse_lazy('cal:tipo_evento_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Novo Tipo de Evento', 'cancel_url': reverse_lazy('cal:tipo_evento_list')})
        return context

class TipoEventoUpdateView(AdminRequiredMixin, UpdateView):
    model = TipoEvento
    form_class = TipoEventoForm
    template_name = 'cal/crud_base_form.html'
    success_url = reverse_lazy('cal:tipo_evento_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': f'Editar Tipo de Evento: {self.object.codigo}', 'cancel_url': reverse_lazy('cal:tipo_evento_list')})
        return context

class TipoEventoDeleteView(AdminRequiredMixin, DeleteView):
    model = TipoEvento
    template_name = 'cal/crud_base_confirm_delete.html'
    success_url = reverse_lazy('cal:tipo_evento_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'titulo': 'Excluir Tipo de Evento', 'cancel_url': reverse_lazy('cal:tipo_evento_list')})
        return context
