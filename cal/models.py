from django.db import models
from django.contrib.auth.models import User
from core.models import Hospital, Setor
from datetime import timedelta, datetime, time
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
# TIPO (Geral)
# =========================
class Tipo(models.Model):
    tipo = models.CharField(max_length=10, verbose_name="Sigla do Tipo")
    tipo_descricao = models.CharField(max_length=50, verbose_name="Descrição do Tipo")
    contabiliza = models.BooleanField(default=True, verbose_name="Contabiliza Carga Horária?")

    class Meta:
        verbose_name = "Tipo"
        verbose_name_plural = "Tipos"
        unique_together = ("tipo", "tipo_descricao")

    def __str__(self):
        return f"{self.tipo} ({self.tipo_descricao})"

# =========================
# TIPO DE EVENTO (Turno)
# =========================
class TipoEvento(models.Model):
    CORES_CHOICES = [
        ('#007bff', 'Azul'),
        ('#6610f2', 'Roxo'),
        ('#6f42c1', 'Lilás'),
        ('#e83e8c', 'Rosa'),
        ('#dc3545', 'Vermelho'),
        ('#fd7e14', 'Laranja'),
        ('#ffc107', 'Amarelo'),
        ('#28a745', 'Verde'),
        ('#20c997', 'Turquesa'),
        ('#17a2b8', 'Ciano'),
        ('#6c757d', 'Cinza'),
        ('#343a40', 'Preto'),
    ]
    tipo_base = models.ForeignKey(Tipo, on_delete=models.CASCADE, related_name="eventos", verbose_name="Tipo Base", null=True, blank=True)
    codigo = models.CharField(max_length=10, verbose_name="Código")
    descricao = models.CharField(max_length=50, verbose_name="Descrição")
    horas = models.PositiveIntegerField(verbose_name="Carga Horária (Horas)")
    cor = models.CharField(max_length=20, choices=CORES_CHOICES, default='#007bff', verbose_name="Cor")
    
    class Meta:
        verbose_name = "Tipo de Evento"
        verbose_name_plural = "Tipos de Evento"
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
    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='matriculas_vinculadas')

    nome_completo = models.CharField(max_length=200)
    nome_exibicao = models.CharField(max_length=50, verbose_name="Nome de Exibição", default="")
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
        ordering = ["nome_exibicao"]

    def __str__(self):
        return f"{self.nome_exibicao} ({self.matricula})"

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
            tipo__tipo_base__contabiliza=True
        )
        return sum(e.tipo.horas for e in eventos)

    def clean(self):
        if self.tipo.tipo_base and self.tipo.tipo_base.contabiliza:
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

# =========================
# ESCALA MENSAL (EXCEL IMPORT)
# =========================
class EscalaMensal(models.Model):
    MES_CHOICES = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
    ]
    mes = models.IntegerField(choices=MES_CHOICES)
    ano = models.IntegerField()
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE)
    arquivo_excel = models.FileField(upload_to='escalas/%Y/%m/', null=True, blank=True)
    criado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Escala Mensal"
        verbose_name_plural = "Escalas Mensais"
        unique_together = ('mes', 'ano', 'hospital', 'setor')

    def __str__(self):
        return f"Escala {self.get_mes_display()}/{self.ano} - {self.hospital} ({self.setor})"

class DiaEscala(models.Model):
    escala = models.ForeignKey(EscalaMensal, on_delete=models.CASCADE, related_name='dias')
    profissional = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    data = models.DateField()
    turnos = models.CharField(max_length=50, blank=True)
    horas_dia = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    e_tpd = models.BooleanField(default=False)
    e_folga = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.profissional} - {self.data} - {self.turnos}"

class ControleSemanal(models.Model):
    escala = models.ForeignKey(EscalaMensal, on_delete=models.CASCADE, related_name='controles')
    profissional = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    semana_numero = models.IntegerField()
    carga_semanal = models.IntegerField(default=40)
    carga_anterior = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    horas_realizadas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    horas_tpd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    horas_tpd_noturno = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def saldo_semanal(self):
        return self.horas_realizadas - self.carga_semanal + self.carga_anterior

    def __str__(self):
        return f"Semana {self.semana_numero} - {self.profissional}"

class MapeamentoTurno(models.Model):
    sigla_excel = models.CharField(max_length=20, unique=True)
    tipo_evento = models.ForeignKey(TipoEvento, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.sigla_excel} -> {self.tipo_evento}"

# =========================
# MÓDULO TPD
# =========================
class TPD(models.Model):
    profissional = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='tpds')
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    horas_trabalhadas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_noturnas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    valor_hora = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    adicional_tpd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    adicional_noturno = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    violacao_regra = models.BooleanField(default=False)
    mensagem_erro = models.TextField(blank=True, null=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT)
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT)

    def __str__(self):
        return f"TPD {self.profissional} - {self.data}"

    def save(self, *args, **kwargs):
        from datetime import datetime, combine
        dt_start = datetime.combine(self.data, self.hora_inicio)
        dt_end = datetime.combine(self.data, self.hora_fim)
        delta = dt_end - dt_start
        self.horas_trabalhadas = delta.total_seconds() / 3600
        self.adicional_tpd = float(self.horas_trabalhadas) * float(self.valor_hora) * 0.5
        super().save(*args, **kwargs)

class LegislacaoTPD(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
