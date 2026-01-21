from django.db import models
from django.contrib.auth.models import User
from core.models import Hospital


class PerfilUsuario(models.Model):
    CHEFE = "CHEFE"
    ESCALANTE = "ESCALANTE"
    PROFISSIONAL = "PROFISSIONAL"
    VISUALIZADOR = "VISUALIZADOR"

    TIPO_CHOICES = [
        (CHEFE, "Chefe"),
        (ESCALANTE, "Escalante"),
        (PROFISSIONAL, "Profissional"),
        (VISUALIZADOR, "Visualizador"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default=PROFISSIONAL
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="usuarios"
    )

    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.tipo})"
