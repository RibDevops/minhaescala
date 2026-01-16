from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse

class Hospital(models.Model):
    nome_hospital = models.CharField(max_length=200)
    sigla = models.CharField(max_length=20, blank=True, null=True)
    def __str__(self):
        return self.nome_hospital

class Setor(models.Model):
    nome_setor = models.CharField(max_length=200)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='setores')
    def __str__(self):
        return f"{self.nome_setor} ({self.hospital.nome_hospital})"

class TipoPlantao(models.Model):
    TIPO_CHOICES = [('NORMAL', 'Normal'), ('TPD', 'TPD')]
    PERIODO_CHOICES = [('SM', 'Manhã'), ('ST', 'Tarde'), ('SN', 'Noite'), ('SD', 'Dia')]
    codigo = models.CharField(max_length=10, unique=True)
    descricao = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    periodo = models.CharField(max_length=2, choices=PERIODO_CHOICES)
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
    pode_visualizar_todos = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_usuario_display()}"

class Enfermeiro(models.Model):
    perfil = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE, related_name='enfermeiro')
    nome_completo = models.CharField(max_length=255)
    matricula = models.CharField(max_length=50, unique=True)
    hospitais = models.ManyToManyField(Hospital, related_name='enfermeiros')
    setores = models.ManyToManyField(Setor, related_name='enfermeiros')
    carga_horaria_mensal = models.IntegerField(default=180)
    
    def __str__(self):
        return self.nome_completo

class Escala(models.Model):
    mes_referencia = models.DateField()
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, related_name='escalas')
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ['mes_referencia', 'setor']

class Plantao(models.Model):
    escala = models.ForeignKey(Escala, on_delete=models.CASCADE, related_name='plantoes')
    enfermeiro = models.ForeignKey(Enfermeiro, on_delete=models.CASCADE, related_name='plantoes')
    tipo_plantao = models.ForeignKey(TipoPlantao, on_delete=models.PROTECT)
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.enfermeiro} - {self.data} - {self.tipo_plantao}"

class Solicitacao(models.Model):
    enfermeiro = models.ForeignKey(Enfermeiro, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20)
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)
    motivo = models.TextField()
    plantao_origem = models.ForeignKey(Plantao, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitacoes_origem')
    enfermeiro_destino = models.ForeignKey(Enfermeiro, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitacoes_destino')
