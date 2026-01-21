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
        ('PROFISSIONAL', 'Enfermeiro'),
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
        return f"{self.user.get_full_name() or self.user.username} ({self.get_tipo_usuario_display()})"

class Especialidade(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Especialidade")

    class Meta:
        verbose_name = "Especialidade"
        verbose_name_plural = "Especialidades"

    def __str__(self):
        return self.nome

class Matricula(models.Model):
    numero = models.CharField(max_length=50, unique=True, verbose_name="Matrícula")
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='matriculas', verbose_name="Perfil", null=True, blank=True)
    nome_exibicao = models.CharField(max_length=50, help_text="Nome como aparecerá no calendário", verbose_name="Nome de Exibição")
    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT, related_name='matriculas', verbose_name="Hospital Vinculado", null=True, blank=True)
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT, related_name='matriculas', verbose_name="Setor Alocado", null=True, blank=True)
    carga_horaria_semanal = models.PositiveIntegerField(default=40, help_text="Limite de horas por semana", verbose_name="Carga Horária Semanal")
    especialidade = models.ForeignKey(Especialidade, on_delete=models.SET_NULL, related_name='matriculas', blank=True, null=True, verbose_name="Especialidade")

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
    cor = models.CharField(max_length=7, default='#3498db', verbose_name="Cor Personalizada", help_text="Cor específica para este evento")
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meus_eventos', verbose_name="Criado por", null=True, blank=True)
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
        super().clean()
        # Regra de Ouro: Enfermeiro só lança para ele mesmo
        if self.criado_por and hasattr(self.criado_por, 'perfil'):
            if self.criado_por.perfil.tipo_usuario == 'PROFISSIONAL':
                # Verifica se a matrícula escolhida pertence ao usuário logado
                if not self.profissional.perfil or self.profissional.perfil.user != self.criado_por:
                    raise ValidationError("Você só pode registrar eventos para sua própria matrícula.")

        if self.profissional_id and self.hospital_id:
            profissional = Matricula.objects.get(id=self.profissional_id)
            hospital = Hospital.objects.get(id=self.hospital_id)
            if profissional.hospital != hospital:
                raise ValidationError(f"O profissional não está vinculado ao hospital {hospital}.")

        if self.setor_id and self.profissional_id:
            profissional = Matricula.objects.get(id=self.profissional_id)
            setor = Setor.objects.get(id=self.setor_id)
            if profissional.setor != setor:
                raise ValidationError(f"O profissional não está alocado no setor {setor}.")

        if self.profissional_id and self.tipo_evento_id:
            tipo_evento = TipoEvento.objects.get(id=self.tipo_evento_id)
            if tipo_evento.contabiliza_carga_horaria:
                horas_acumuladas = self.calcular_horas_semanais_acumuladas()
                nova_soma = horas_acumuladas + tipo_evento.horas
                profissional = Matricula.objects.get(id=self.profissional_id)
                if nova_soma > profissional.carga_horaria_semanal:
                    raise ValidationError(f"Alerta: Excesso de carga horária! O profissional já possui {horas_acumuladas}h nos últimos 7 dias. Com este evento, chegará a {nova_soma}h (Limite: {profissional.carga_horaria_semanal}h).")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profissional.nome_exibicao} | {self.tipo_evento.codigo} | {self.setor.nome}"
