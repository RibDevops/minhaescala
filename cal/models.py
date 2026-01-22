from django.db import models
from django.contrib.auth.models import User
from core.models import Hospital, Setor
from datetime import timedelta
from django.core.exceptions import ValidationError

# =========================
# PERÍODO
# =========================
class Periodo(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Nome do Período")
    sigla = models.CharField(max_length=10, verbose_name="Sigla")

    class Meta:
        verbose_name = "Período"
        verbose_name_plural = "Períodos"

    def __str__(self):
        return self.nome

# =========================
# ESPECIALIDADE
# =========================
class Especialidade(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Especialidade")

    class Meta:
        verbose_name = "Especialidade"
        verbose_name_plural = "Especialidades"

    def __str__(self):
        return self.nome

# =========================
# TIPO DE TURNO (TIPO DE EVENTO)
# =========================
class TipoEvento(models.Model):
    codigo = models.CharField(max_length=10)
    descricao = models.CharField(max_length=50)
    horas = models.PositiveIntegerField()
    cor = models.CharField(max_length=20, default="primary")
    contabiliza = models.BooleanField(default=True)

    class Meta:
        unique_together = ("codigo", "descricao")

    def __str__(self):
        return f"{self.codigo} ({self.horas}h)"

# =========================
# PERFIL DE USUÁRIO
# =========================
class PerfilUsuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('ESCALANTE', 'Escalante'),
        ('ENFERMEIRO', 'Enfermeiro'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cal_perfil')
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='ENFERMEIRO')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_display()}"

# =========================
# PROFISSIONAL (MATRÍCULA)
# =========================
class Matricula(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="matricula",
        null=True,
        blank=True
    )
    # Adicionado para facilitar o acesso ao perfil
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='matriculas_vinculadas')

    nome_completo = models.CharField(max_length=200)
    nome_guerra = models.CharField(max_length=50)
    matricula = models.CharField(max_length=30, unique=True)
    coren = models.CharField(max_length=30, blank=True, null=True)

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="profissionais"
    )

    setor = models.ForeignKey(
        Setor,
        on_delete=models.PROTECT,
        related_name="profissionais",
        null=True,
        blank=True
    )
    especialidade = models.ForeignKey(
        Especialidade,
        on_delete=models.SET_NULL,
        related_name="profissionais",
        null=True,
        blank=True
    )

    carga_horaria_semanal = models.PositiveIntegerField(default=40)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome_guerra"]

    def __str__(self):
        return f"{self.nome_guerra} ({self.matricula})"

# =========================
# EVENTO DE ESCALA
# =========================
class EventoEscala(models.Model):
    data = models.DateField()
    profissional = models.ForeignKey(
        Matricula,
        on_delete=models.CASCADE,
        related_name="eventos"
    )
    tipo = models.ForeignKey(
        TipoEvento,
        on_delete=models.PROTECT
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT
    )
    setor = models.ForeignKey(
        Setor,
        on_delete=models.PROTECT
    )
    criado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="eventos_criados"
    )
    observacao = models.TextField(blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def carga_ultimos_7_dias(self):
        inicio = self.data - timedelta(days=7)
        eventos = EventoEscala.objects.filter(
            profissional=self.profissional,
            data__range=(inicio, self.data),
            tipo__contabiliza=True
        )
        return sum(e.tipo.horas for e in eventos)

    def clean(self):
        if self.tipo.contabiliza:
            total = self.carga_ultimos_7_dias() + self.tipo.horas
            if total > self.profissional.carga_horaria_semanal:
                raise ValidationError(
                    f"Excesso de carga semanal ({total}h)"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profissional} - {self.tipo} - {self.data}"
