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


# ---------------------------------------------------------------------------
# TPD tests
# ---------------------------------------------------------------------------
from django.core.exceptions import ValidationError as DjangoValidationError
from cal.models import TPD, Matricula, PerfilUsuario as CalPerfil, LIMITE_HORAS_MENSAIS_TPD
import datetime


class TPDModelTests(TestCase):
    def setUp(self):
        self.hospital = Hospital.objects.create(nome="H TPD", sigla="HT")
        from core.models import Setor
        self.setor = Setor.objects.create(nome="UTI", hospital=self.hospital)

        user = User.objects.create_user(username="prof1", password="x")
        perfil = CalPerfil.objects.create(user=user, tipo='ENFERMEIRO')
        self.matricula = Matricula.objects.create(
            user=user,
            nome_completo="Profissional Um",
            nome_exibicao="Prof Um",
            matricula="M001",
            hospital=self.hospital,
            setor=self.setor,
            perfil=perfil,
        )

    def _make_tpd(self, hora_inicio="07:00", hora_fim="13:00", mes=1, ano=2025):
        return TPD(
            profissional=self.matricula,
            data=datetime.date(ano, mes, 10),
            hora_inicio=datetime.time(*map(int, hora_inicio.split(":"))),
            hora_fim=datetime.time(*map(int, hora_fim.split(":"))),
            hospital=self.hospital,
            setor=self.setor,
        )

    def test_horas_trabalhadas_calculadas_no_save(self):
        tpd = self._make_tpd("07:00", "13:00")
        tpd.save()
        self.assertEqual(float(tpd.horas_trabalhadas), 6.0)

    def test_adicional_tpd_calculado_no_save(self):
        tpd = self._make_tpd("07:00", "13:00")  # 6h × 50 × 0.5 = 150
        tpd.save()
        self.assertEqual(float(tpd.adicional_tpd), 150.0)

    def test_hora_fim_antes_inicio_invalido(self):
        tpd = self._make_tpd("13:00", "07:00")
        with self.assertRaises(DjangoValidationError):
            tpd.full_clean()

    def test_limite_mensal_bloqueado(self):
        """Não deve permitir ultrapassar LIMITE_HORAS_MENSAIS_TPD no mês."""
        # Cria TPDs que somam exatamente o limite
        for dia in range(1, 9):  # 8 dias × 5h = 40h
            t = TPD(
                profissional=self.matricula,
                data=datetime.date(2025, 3, dia),
                hora_inicio=datetime.time(7, 0),
                hora_fim=datetime.time(12, 0),
                hospital=self.hospital,
                setor=self.setor,
            )
            t.save()

        # Mais 5h = 45h > 44h → deve falhar
        tpd_extra = TPD(
            profissional=self.matricula,
            data=datetime.date(2025, 3, 9),
            hora_inicio=datetime.time(7, 0),
            hora_fim=datetime.time(12, 0),
            hospital=self.hospital,
            setor=self.setor,
        )
        with self.assertRaises(DjangoValidationError):
            tpd_extra.full_clean()

    def test_limite_mensal_permite_exato(self):
        """Deve permitir TPDs que somam exatamente o limite."""
        # 44h em 4 blocos de 11h
        for dia in range(1, 5):
            t = TPD(
                profissional=self.matricula,
                data=datetime.date(2025, 4, dia),
                hora_inicio=datetime.time(7, 0),
                hora_fim=datetime.time(18, 0),
                hospital=self.hospital,
                setor=self.setor,
            )
            t.save()
        total = TPD.objects.filter(
            profissional=self.matricula,
            data__year=2025,
            data__month=4,
        ).count()
        self.assertEqual(total, 4)

    def test_limite_mensal_independente_por_mes(self):
        """O limite é por mês; meses diferentes não interferem."""
        for dia in range(1, 9):  # 40h em março
            TPD(
                profissional=self.matricula,
                data=datetime.date(2025, 3, dia),
                hora_inicio=datetime.time(7, 0),
                hora_fim=datetime.time(12, 0),
                hospital=self.hospital,
                setor=self.setor,
            ).save()

        # Abril começa do zero — 5h deve passar
        tpd_abril = TPD(
            profissional=self.matricula,
            data=datetime.date(2025, 4, 1),
            hora_inicio=datetime.time(7, 0),
            hora_fim=datetime.time(12, 0),
            hospital=self.hospital,
            setor=self.setor,
        )
        tpd_abril.save()  # não deve lançar exceção
        self.assertIsNotNone(tpd_abril.pk)
