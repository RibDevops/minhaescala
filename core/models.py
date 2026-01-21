from django.db import models
from django.contrib.auth.models import User


class Hospital(models.Model):
    nome = models.CharField(max_length=150, unique=True)
    sigla = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.sigla or self.nome


class Setor(models.Model):
    nome = models.CharField(max_length=100)
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="setores"
    )

    class Meta:
        unique_together = ("nome", "hospital")

    def __str__(self):
        return f"{self.nome} - {self.hospital}"


class Auditoria(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="auditorias"
    )
    acao = models.CharField(max_length=255)
    data = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"{self.usuario} - {self.acao}"
