from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import timedelta

class Hospital(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Hospital")
    sigla = models.CharField(max_length=20, blank=True, null=True, verbose_name="Sigla")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitais"

class Setor(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Nome do Setor")
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='setores', verbose_name="Hospital")

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"
        unique_together = ['nome', 'hospital']

    def __str__(self):
        return f"{self.nome} ({self.hospital.sigla or self.hospital.nome})"

class Periodo(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Nome do Período")
    sigla = models.CharField(max_length=10, verbose_name="Sigla")

    class Meta:
        verbose_name = "Período"
        verbose_name_plural = "Períodos"

    def __str__(self):
        return self.nome

class TipoEvento(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Nome do Tipo de Evento")
    codigo = models.CharField(max_length=20, verbose_name="Código/Sigla")
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='tipos_evento', verbose_name="Período")
    horas = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(24)], verbose_name="Carga Horária")
    cor = models.CharField(max_length=7, default='#3498db', verbose_name="Cor no Calendário")
    contabiliza_carga_horaria = models.BooleanField(default=True, verbose_name="Contabiliza Carga Horária?")

    class Meta:
        verbose_name = "Tipo de Evento"
        verbose_name_plural = "Tipos de Eventos"

    def __str__(self):
        return f"{self.codigo} - {self.periodo.sigla} ({self.horas}h)"

class PerfilUsuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('PROFISSIONAL', 'Profissional'),
        ('ESCALANTE', 'Escalante'),
        ('CHEFE', 'Chefe de Setor'),
        ('ADMIN', 'Administrador'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', verbose_name="Usuário")
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='PROFISSIONAL', verbose_name="Nível de Acesso")

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Especialidade(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Especialidade")

    class Meta:
        verbose_name = "Especialidade"
        verbose_name_plural = "Especialidades"

    def __str__(self):
        return self.nome

class Matricula(models.Model):
    numero = models.CharField(max_length=50, unique=True, verbose_name="Número da Matrícula")
    perfil = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE, related_name='matricula', verbose_name="Perfil")
    nome_exibicao = models.CharField(max_length=50, help_text="Nome como aparecerá no calendário", verbose_name="Nome de Exibição")
    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    hospitais = models.ManyToManyField(Hospital, related_name='matriculas', verbose_name="Hospitais Vinculados")
    setores = models.ManyToManyField(Setor, related_name='matriculas', verbose_name="Setores Alocados")
    carga_horaria_semanal = models.PositiveIntegerField(default=40, help_text="Limite de horas por semana", verbose_name="Carga Horária Semanal")
    especialidades = models.ManyToManyField(Especialidade, related_name='matriculas', blank=True, verbose_name="Especialidades")

    class Meta:
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"

    def __str__(self):
        return f"{self.nome_exibicao} ({self.numero})"

class EventoEscala(models.Model):
    data = models.DateField(verbose_name="Data")
    profissional = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='eventos', verbose_name="Profissional")
    tipo_evento = models.ForeignKey(TipoEvento, on_delete=models.PROTECT, related_name='eventos', verbose_name="Tipo de Evento")
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='eventos', verbose_name="Hospital")
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, related_name='eventos', verbose_name="Setor")
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Criado por")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Evento de Escala"
        verbose_name_plural = "Eventos de Escala"

    def calcular_horas_semanais_acumuladas(self):
        data_inicio = self.data - timedelta(days=7)
        eventos = EventoEscala.objects.filter(
            profissional=self.profissional,
            data__range=[data_inicio, self.data - timedelta(days=1)],
            tipo_evento__contabiliza_carga_horaria=True
        )
        return sum(e.tipo_evento.horas for e in eventos)

    def clean(self):
        if self.profissional_id and self.hospital_id:
            if not self.profissional.hospitais.filter(id=self.hospital.id).exists():
                raise ValidationError(f"O profissional não está vinculado ao hospital {self.hospital}.")

        if self.setor_id and self.profissional_id:
            if not self.profissional.setores.filter(id=self.setor.id).exists():
                raise ValidationError(f"O profissional não está alocado no setor {self.setor}.")

        if self.profissional_id and self.tipo_evento_id and self.tipo_evento.contabiliza_carga_horaria:
            horas_acumuladas = self.calcular_horas_semanais_acumuladas()
            nova_soma = horas_acumuladas + self.tipo_evento.horas
            if nova_soma > self.profissional.carga_horaria_semanal:
                raise ValidationError(f"Alerta: Excesso de carga horária! O profissional já possui {horas_acumuladas}h nos últimos 7 dias. Com este evento, chegará a {nova_soma}h (Limite: {self.profissional.carga_horaria_semanal}h).")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profissional.nome_exibicao} | {self.tipo_evento.codigo} | {self.setor.nome}"
