"""
Helpers e mixins de permissão centralizados para o app cal.

Hierarquia de papéis:
  is_staff / ADMIN  → acesso total
  ESCALANTE         → acesso ao próprio hospital+setor (sem ver registros privados de enfermeiros)
  ENFERMEIRO        → acesso aos próprios registros privados + registros oficiais do seu setor
"""

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# ---------------------------------------------------------------------------
# Helpers de perfil
# ---------------------------------------------------------------------------

def get_perfil(user):
    """Retorna o cal.PerfilUsuario do usuário, ou None."""
    return getattr(user, 'cal_perfil', None)


def get_matricula(user):
    """Retorna a Matricula vinculada ao usuário, ou None."""
    return getattr(user, 'matricula', None)


def is_admin(user):
    """True para is_staff ou papel ADMIN."""
    perfil = get_perfil(user)
    return user.is_staff or (perfil is not None and perfil.tipo == 'ADMIN')


def is_escalante(user):
    """True apenas para papel ESCALANTE (não inclui admin)."""
    perfil = get_perfil(user)
    return perfil is not None and perfil.tipo == 'ESCALANTE'


def is_enfermeiro(user):
    """True apenas para papel ENFERMEIRO."""
    perfil = get_perfil(user)
    return perfil is not None and perfil.tipo == 'ENFERMEIRO'


def is_escalante_ou_admin(user):
    return is_admin(user) or is_escalante(user)


def mesmo_setor(user, obj_hospital, obj_setor):
    """
    Verifica se o usuário pertence ao mesmo hospital+setor do objeto.
    Usado para restringir escalantes ao seu próprio setor.
    """
    matricula = get_matricula(user)
    if not matricula:
        return False
    return matricula.hospital_id == obj_hospital.id and matricula.setor_id == obj_setor.id


# ---------------------------------------------------------------------------
# Mixins para class-based views
# ---------------------------------------------------------------------------

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Permite acesso apenas a is_staff ou papel ADMIN."""

    def test_func(self):
        return is_admin(self.request.user)


class EscalanteOuAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Permite acesso a ESCALANTE e ADMIN/is_staff."""

    def test_func(self):
        return is_escalante_ou_admin(self.request.user)


class MesmoSetorOuAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Permite acesso a admin ou ao escalante do mesmo setor do objeto.
    A view deve implementar `get_object_hospital_setor()` retornando (hospital, setor).
    """

    def get_object_hospital_setor(self):
        raise NotImplementedError("Implemente get_object_hospital_setor() na view.")

    def test_func(self):
        user = self.request.user
        if is_admin(user):
            return True
        if is_escalante(user):
            hospital, setor = self.get_object_hospital_setor()
            return mesmo_setor(user, hospital, setor)
        return False


# ---------------------------------------------------------------------------
# Helpers para function-based views
# ---------------------------------------------------------------------------

def exige_escalante_ou_admin(user):
    """Lança PermissionDenied se o usuário não for escalante nem admin."""
    if not is_escalante_ou_admin(user):
        raise PermissionDenied


def exige_admin(user):
    """Lança PermissionDenied se o usuário não for admin."""
    if not is_admin(user):
        raise PermissionDenied


def exige_mesmo_setor_ou_admin(user, hospital, setor):
    """Lança PermissionDenied se o usuário não for admin nem escalante do mesmo setor."""
    if is_admin(user):
        return
    if is_escalante(user) and mesmo_setor(user, hospital, setor):
        return
    raise PermissionDenied
