from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Hospital
from .models import PerfilUsuario


class PerfilUsuarioSignalTests(TestCase):
    def setUp(self):
        self.hospital = Hospital.objects.create(nome="Hospital Teste", sigla="HT")

    def test_perfil_created_on_user_creation(self):
        """PerfilUsuario is auto-created when a new User is saved."""
        user = User.objects.create_user(username="joao", password="pass123")
        self.assertTrue(
            PerfilUsuario.objects.filter(user=user).exists(),
            "PerfilUsuario should be created automatically via post_save signal.",
        )

    def test_perfil_linked_to_correct_user(self):
        """The auto-created PerfilUsuario references the correct User."""
        user = User.objects.create_user(username="maria", password="pass123")
        perfil = PerfilUsuario.objects.get(user=user)
        self.assertEqual(perfil.user, user)

    def test_perfil_default_tipo_is_profissional(self):
        """New profiles default to the PROFISSIONAL role."""
        user = User.objects.create_user(username="pedro", password="pass123")
        perfil = PerfilUsuario.objects.get(user=user)
        self.assertEqual(perfil.tipo, PerfilUsuario.PROFISSIONAL)

    def test_perfil_assigned_first_hospital(self):
        """New profiles are assigned the first Hospital in the database."""
        user = User.objects.create_user(username="ana", password="pass123")
        perfil = PerfilUsuario.objects.get(user=user)
        self.assertEqual(perfil.hospital, Hospital.objects.first())

    def test_perfil_not_duplicated_on_user_update(self):
        """Saving an existing User does not create a second PerfilUsuario."""
        user = User.objects.create_user(username="carlos", password="pass123")
        user.first_name = "Carlos"
        user.save()
        count = PerfilUsuario.objects.filter(user=user).count()
        self.assertEqual(count, 1, "Only one PerfilUsuario should exist per user.")

    def test_perfil_active_by_default(self):
        """New profiles are active by default."""
        user = User.objects.create_user(username="lucia", password="pass123")
        perfil = PerfilUsuario.objects.get(user=user)
        self.assertTrue(perfil.ativo)

    def test_perfil_str(self):
        """PerfilUsuario.__str__ returns username and tipo."""
        user = User.objects.create_user(username="roberto", password="pass123")
        perfil = PerfilUsuario.objects.get(user=user)
        self.assertIn("roberto", str(perfil))
        self.assertIn(perfil.tipo, str(perfil))
