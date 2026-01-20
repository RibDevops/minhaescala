from django.urls import path, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from cal.models import Hospital, Setor, Periodo, TipoEvento, Especialidade, Matricula

# Mixin para garantir acesso apenas a staff/admin nos CRUDs de configuração
class AdminRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = 'is_staff'
    def has_permission(self):
        return self.request.user.is_staff

# Hospital
class HospitalListView(AdminRequiredMixin, ListView):
    model = Hospital
    template_name = 'cal/hospital/list.html'
    context_object_name = 'objetos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Hospitais',
            'labels': ['Nome', 'Sigla'],
            'create_url': 'cal:hospital_create',
            'update_url': 'cal:hospital_update',
            'delete_url': 'cal:hospital_delete',
        })
        return context

class HospitalCreateView(AdminRequiredMixin, CreateView):
    model = Hospital
    fields = ['nome', 'sigla']
    template_name = 'cal/hospital/form.html'
    success_url = reverse_lazy('cal:hospital_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Novo Hospital',
            'cancel_url': reverse_lazy('cal:hospital_list'),
        })
        return context

class HospitalUpdateView(AdminRequiredMixin, UpdateView):
    model = Hospital
    fields = ['nome', 'sigla']
    template_name = 'cal/hospital/form.html'
    success_url = reverse_lazy('cal:hospital_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': f'Editar Hospital: {self.object.nome}',
            'cancel_url': reverse_lazy('cal:hospital_list'),
        })
        return context

class HospitalDeleteView(AdminRequiredMixin, DeleteView):
    model = Hospital
    template_name = 'cal/hospital/confirm_delete.html'
    success_url = reverse_lazy('cal:hospital_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Excluir Hospital',
            'cancel_url': reverse_lazy('cal:hospital_list'),
        })
        return context

# Setor
class SetorListView(AdminRequiredMixin, ListView):
    model = Setor
    template_name = 'cal/setor/list.html'
    context_object_name = 'objetos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Setores',
            'labels': ['Nome', 'Hospital'],
            'create_url': 'cal:setor_create',
            'update_url': 'cal:setor_update',
            'delete_url': 'cal:setor_delete',
        })
        return context

class SetorCreateView(AdminRequiredMixin, CreateView):
    model = Setor
    fields = ['nome', 'hospital']
    template_name = 'cal/setor/form.html'
    success_url = reverse_lazy('cal:setor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Novo Setor',
            'cancel_url': reverse_lazy('cal:setor_list'),
        })
        return context

class SetorUpdateView(AdminRequiredMixin, UpdateView):
    model = Setor
    fields = ['nome', 'hospital']
    template_name = 'cal/setor/form.html'
    success_url = reverse_lazy('cal:setor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': f'Editar Setor: {self.object.nome}',
            'cancel_url': reverse_lazy('cal:setor_list'),
        })
        return context

class SetorDeleteView(AdminRequiredMixin, DeleteView):
    model = Setor
    template_name = 'cal/setor/confirm_delete.html'
    success_url = reverse_lazy('cal:setor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Excluir Setor',
            'cancel_url': reverse_lazy('cal:setor_list'),
        })
        return context

# Matricula
class MatriculaListView(AdminRequiredMixin, ListView):
    model = Matricula
    template_name = 'cal/matricula/list.html'
    context_object_name = 'objetos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Matrículas',
            'labels': ['Número', 'Nome de Exibição', 'Carga Horária'],
            'create_url': 'cal:matricula_create',
            'update_url': 'cal:matricula_update',
            'delete_url': 'cal:matricula_delete',
        })
        return context

class MatriculaCreateView(AdminRequiredMixin, CreateView):
    model = Matricula
    fields = ['numero', 'perfil', 'nome_exibicao', 'nome_completo', 'hospitais', 'setores', 'carga_horaria_semanal', 'especialidades']
    template_name = 'cal/matricula/form.html'
    success_url = reverse_lazy('cal:matricula_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Nova Matrícula',
            'cancel_url': reverse_lazy('cal:matricula_list'),
        })
        return context

class MatriculaUpdateView(AdminRequiredMixin, UpdateView):
    model = Matricula
    fields = ['numero', 'perfil', 'nome_exibicao', 'nome_completo', 'hospitais', 'setores', 'carga_horaria_semanal', 'especialidades']
    template_name = 'cal/matricula/form.html'
    success_url = reverse_lazy('cal:matricula_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': f'Editar Matrícula: {self.object.numero}',
            'cancel_url': reverse_lazy('cal:matricula_list'),
        })
        return context

class MatriculaDeleteView(AdminRequiredMixin, DeleteView):
    model = Matricula
    template_name = 'cal/matricula/confirm_delete.html'
    success_url = reverse_lazy('cal:matricula_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Excluir Matrícula',
            'cancel_url': reverse_lazy('cal:matricula_list'),
        })
        return context
