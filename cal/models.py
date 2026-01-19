from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse


class Hospital(models.Model):
    nome_hospital = models.CharField(max_length=50, unique=True)
    nome_hospital_sigla = models.CharField(max_length=20, blank=True, null=True, related_name='Sigla Hospital')
    def __str__(self):
        return self.nome_hospital

class Setor(models.Model):
    nome_setor = models.CharField(max_length=50, related_name='Setor')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='Hospital setor')
    def __str__(self):
        return f"{self.nome_setor} ({self.hospital.nome_hospital})"

class Periodo(models.Model):
    periodo_evento = models.CharField(max_length=50, related_name='Periodo')
    periodo_evento_sigla = models.CharField(max_length=10, related_name='Sigla Evento')

-> vamos alterar o tipo de plantão para evento, assim podemos incluir outros tipos de eventos futuramente, como treinamentos, reuniões, folgas, abonos, etc.

class TipoEvento(models.Model):
    tipo_evento = models.CharField(max_length=50, related_name='Tipo Evento')
    tipo_evento_sigla = models.CharField(max_length=20, related_name='Sigla Tipo Evento')

    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='Período  Evento')

    horas = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(24)])
    cor = models.CharField(max_length=7, default='#3498db')

    def __str__(self):
        return f"{self.codigo} - {self.descricao} ({self.horas}h)"

class PerfilUsuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('PROFISSIONAL', 'Profissional'),
        ('ESCALANTE', 'Escalante'),
        ('CHEFE', 'Chefe de Setor'),
        ('ADMIN', 'Administrador'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='PROFISSIONAL')
    pode_escalar = models.BooleanField(default=False)
    pode_aprovar = models.BooleanField(default=False)
    pode_visualizar_todos = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_usuario_display()}"

class Especialidade(models.Model):
    nome = models.CharField(max_length=100)
    def __str__(self):
        return self.nome

class Matricula(models.Model):
    matricula = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.matricula

-> precisamo alterar a forma de armazenar os enfermeiros, para incluir mais de uma matricula por enfermeiro, assim como permitir que um enfermeiro trabalhe em mais de um hospital e setor.
class Enfermeiro(models.Model):
    perfil = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE, related_name='enfermeiro_perfil')
    nome_completo = models.CharField(max_length=255)
    nome = models.CharField(max_length=50, default='')
    matriculas = models.ManyToManyField('Matricula', related_name='Enfermeiro matriculas')
    hospitais = models.ManyToManyField(Hospital, related_name='Hospital enfermeiros')
    setores = models.ManyToManyField(Setor, related_name='Setor enfermeiros')
    carga_horaria_mensal = models.IntegerField(default=180, related_name='Carga horária mensal')
    especialidade = models.ManyToManyField(Especialidade, related_name='Enfermeiros especialidades', blank=True)

    def __str__(self):
        return self.nome_completo

class Escala(models.Model):
    mes_referencia = models.DateField()
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, related_name='escalas')
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ['mes_referencia', 'setor']

-> no momnto de inserir os plantões, precisamos relacionar o escalante com Hospital, escalante com Setor, enfermeiro com Hospital e enfermeiro com Setor.
-> temos resolver, se um enfermeiro pode trabalhar em mais de um hospital e setor, como vamos fazer para relacionar o plantão com o hospital e setor corretos.
-> o usario pode selecionar o hospital e setor na hora de criar o plantão, mas precisamos garantir que o enfermeiro selecionado realmente trabalha naquele hospital e setor.

class Plantao(models.Model):
    escala = models.ForeignKey(Escala, on_delete=models.CASCADE, related_name='plantoes')
    enfermeiro = models.ForeignKey(Enfermeiro, on_delete=models.CASCADE, related_name='plantoes')
    tipo_evento = models.ForeignKey(TipoEvento, on_delete=models.PROTECT)
    data = models.DateField()
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.enfermeiro} - {self.data} - {self.tipo_evento}"

class Solicitacao(models.Model):
   ** remover essa class e suas fuções nao vamos usar solcitações


