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

class HospitalCreateView(AdminRequiredMixin, CreateView):
    model = Hospital
    fields = ['nome', 'sigla']
    template_name = 'cal/hospital/form.html'
    success_url = reverse_lazy('cal:hospital_list')

class HospitalUpdateView(AdminRequiredMixin, UpdateView):
    model = Hospital
    fields = ['nome', 'sigla']
    template_name = 'cal/hospital/form.html'
    success_url = reverse_lazy('cal:hospital_list')

class HospitalDeleteView(AdminRequiredMixin, DeleteView):
    model = Hospital
    template_name = 'cal/hospital/confirm_delete.html'
    success_url = reverse_lazy('cal:hospital_list')

# Setor
class SetorListView(AdminRequiredMixin, ListView):
    model = Setor
    template_name = 'cal/setor/list.html'
    context_object_name = 'objetos'

class SetorCreateView(AdminRequiredMixin, CreateView):
    model = Setor
    fields = ['nome', 'hospital']
    template_name = 'cal/setor/form.html'
    success_url = reverse_lazy('cal:setor_list')

class SetorUpdateView(AdminRequiredMixin, UpdateView):
    model = Setor
    fields = ['nome', 'hospital']
    template_name = 'cal/setor/form.html'
    success_url = reverse_lazy('cal:setor_list')

class SetorDeleteView(AdminRequiredMixin, DeleteView):
    model = Setor
    template_name = 'cal/setor/confirm_delete.html'
    success_url = reverse_lazy('cal:setor_list')

# Matricula
class MatriculaListView(AdminRequiredMixin, ListView):
    model = Matricula
    template_name = 'cal/matricula/list.html'
    context_object_name = 'objetos'

class MatriculaCreateView(AdminRequiredMixin, CreateView):
    model = Matricula
    fields = ['numero', 'perfil', 'nome_exibicao', 'nome_completo', 'hospitais', 'setores', 'carga_horaria_semanal', 'especialidades']
    template_name = 'cal/matricula/form.html'
    success_url = reverse_lazy('cal:matricula_list')

class MatriculaUpdateView(AdminRequiredMixin, UpdateView):
    model = Matricula
    fields = ['numero', 'perfil', 'nome_exibicao', 'nome_completo', 'hospitais', 'setores', 'carga_horaria_semanal', 'especialidades']
    template_name = 'cal/matricula/form.html'
    success_url = reverse_lazy('cal:matricula_list')

class MatriculaDeleteView(AdminRequiredMixin, DeleteView):
    model = Matricula
    template_name = 'cal/matricula/confirm_delete.html'
    success_url = reverse_lazy('cal:matricula_list')
