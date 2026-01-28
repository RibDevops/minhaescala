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
# TIPO (TIPO)
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
# TIPO DE TURNO (TIPO DE EVENTO)
# =========================
class TipoEvento(models.Model):
    tipo_base = models.ForeignKey(Tipo, on_delete=models.CASCADE, related_name="eventos", verbose_name="Tipo Base", null=True, blank=True)
    codigo = models.CharField(max_length=10, verbose_name="Código")
    descricao = models.CharField(max_length=50, verbose_name="Descrição")
    horas = models.PositiveIntegerField(verbose_name="Carga Horária (Horas)")
    cor = models.CharField(max_length=20, default="primary", verbose_name="Cor")
    
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
    # Adicionado para facilitar o acesso ao perfil
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
        if self.tipo.tipo_base.contabiliza:
            total = self.carga_ultimos_7_dias() + self.tipo.horas
            if total > self.profissional.carga_horaria_semanal:
                raise ValidationError(
                    f"Excesso de carga semanal ({total}h)"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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
        # Lógica simplificada de cálculo para MVP
        from datetime import datetime, combine
        start = combine(self.data, self.hora_inicio)
        end = combine(self.data, self.hora_fim)
        delta = end - start
        self.horas_trabalhadas = delta.total_seconds() / 3600
        self.adicional_tpd = float(self.horas_trabalhadas) * float(self.valor_hora) * 0.5
        super().save(*args, **kwargs)

# models.py
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

class LegislaçãoTPD(models.Model):
    """Armazena as regras legais"""
    nome = models.CharField(max_length=100)
    descricao = models.TextField()

    # REGRAS PRINCIPAIS (conforme legislação)
    limite_diario = models.IntegerField(default=8)  # 8h por dia (Lei 8.112/90)
    limite_mensal = models.IntegerField(default=44)  # 44h por mês (Portaria SES-DF)
    intervalo_minimo = models.IntegerField(default=11)  # 11h entre jornadas

    def __str__(self):
        return self.nome

class Profissional(models.Model):
    """Dados do profissional"""
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20)
    carga_horaria_semanal = models.IntegerField(default=40)

    def __str__(self):
        return f"{self.nome} ({self.matricula})"

class TPD(models.Model):
    """Registro de TPD"""
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    motivo = models.CharField(max_length=100)

    # Calculados automaticamente
    horas_trabalhadas = models.FloatField(default=0)
    horas_noturnas = models.FloatField(default=0)
    adicional_tpd = models.FloatField(default=0)
    adicional_noturno = models.FloatField(default=0)

    # Status de validação
    violacao_regra = models.BooleanField(default=False)
    mensagem_erro = models.TextField(blank=True)

    data_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data']

    def calcular_horas(self):
        """Calcula horas trabalhadas"""
        inicio = datetime.combine(self.data, self.hora_inicio)
        fim = datetime.combine(self.data, self.hora_fim)

        # Se passou da meia-noite
        if fim < inicio:
            fim = fim + timedelta(days=1)

        horas = (fim - inicio).total_seconds() / 3600
        return round(horas, 2)

    def calcular_horas_noturnas(self):
        """Calcula horas entre 22h e 6h"""
        horas_noturnas = 0
        hora_atual = self.hora_inicio

        # Converte para datetime para facilitar cálculo
        inicio = datetime.combine(self.data, self.hora_inicio)
        fim = datetime.combine(self.data, self.hora_fim)
        if fim < inicio:
            fim = fim + timedelta(days=1)

        # Define período noturno
        noturno_inicio = datetime.combine(self.data, datetime.strptime('22:00', '%H:%M').time())
        noturno_fim = datetime.combine(self.data, datetime.strptime('06:00', '%H:%M').time())
        noturno_fim = noturno_fim + timedelta(days=1)  # Ajusta para após meia-noite

        # Calcula sobreposição
        inicio_overlap = max(inicio, noturno_inicio)
        fim_overlap = min(fim, noturno_fim)

        if inicio_overlap < fim_overlap:
            horas_noturnas = (fim_overlap - inicio_overlap).total_seconds() / 3600

        return round(horas_noturnas, 2)

    def verificar_regras(self):
        """Verifica todas as regras legais"""
        erros = []

        # 1. Verifica intervalo mínimo de 11h
        tpd_anterior = TPD.objects.filter(
            profissional=self.profissional,
            data=self.data
        ).exclude(id=self.id).order_by('-hora_fim').first()

        if tpd_anterior:
            intervalo = self.tempo_entre_jornadas(tpd_anterior)
            if intervalo < 11:
                erros.append(f"Intervalo mínimo violado: {intervalo}h (mínimo 11h)")

        # 2. Verifica limite diário (8h)
        horas_hoje = self.horas_do_dia()
        if horas_hoje > 8:
            erros.append(f"Limite diário excedido: {horas_hoje}h (máximo 8h)")

        # 3. Verifica limite mensal (44h)
        horas_mes = self.horas_do_mes()
        if horas_mes > 44:
            erros.append(f"Limite mensal excedido: {horas_mes}h (máximo 44h)")

        # Atualiza status
        self.violacao_regra = len(erros) > 0
        self.mensagem_erro = " | ".join(erros)

        return len(erros) == 0

    def tempo_entre_jornadas(self, tpd_anterior):
        """Calcula tempo entre o fim da jornada anterior e início da atual"""
        fim_anterior = datetime.combine(tpd_anterior.data, tpd_anterior.hora_fim)
        inicio_atual = datetime.combine(self.data, self.hora_inicio)

        if inicio_atual < fim_anterior:
            inicio_atual = inicio_atual + timedelta(days=1)

        intervalo = (inicio_atual - fim_anterior).total_seconds() / 3600
        return intervalo

    def horas_do_dia(self):
        """Soma todas as horas trabalhadas no dia"""
        tpd_dia = TPD.objects.filter(
            profissional=self.profissional,
            data=self.data
        )

        total = sum(t.horas_trabalhadas for t in tpd_dia)
        return total

    def horas_do_mes(self):
        """Soma todas as horas trabalhadas no mês"""
        inicio_mes = self.data.replace(day=1)
        if self.data.month == 12:
            fim_mes = self.data.replace(year=self.data.year + 1, month=1, day=1)
        else:
            fim_mes = self.data.replace(month=self.data.month + 1, day=1)

        tpd_mes = TPD.objects.filter(
            profissional=self.profissional,
            data__gte=inicio_mes,
            data__lt=fim_mes
        )

        total = sum(t.horas_trabalhadas for t in tpd_mes)
        return total

    def calcular_adicional(self):
        """Calcula adicionais de TPD (50%) e noturno (20%)"""
        horas_normais = self.horas_trabalhadas - self.horas_noturnas

        # Valor base fictício (R$ 50/hora)
        valor_hora = 50.00

        # Adicional TPD: 50% sobre todas as horas
        self.adicional_tpd = (self.horas_trabalhadas * valor_hora) * 0.5

        # Adicional noturno: 20% sobre horas noturnas
        self.adicional_noturno = (self.horas_noturnas * valor_hora) * 0.2

        return self.adicional_tpd + self.adicional_noturno

    def save(self, *args, **kwargs):
        """Sobrescreve save para cálculos automáticos"""
        # Calcula horas
        self.horas_trabalhadas = self.calcular_horas()
        self.horas_noturnas = self.calcular_horas_noturnas()

        # Verifica regras
        self.verificar_regras()

        # Calcula adicionais
        self.calcular_adicional()

        super().save(*args, **kwargs)

    def __str__(self):
        status = "⚠️" if self.violacao_regra else "✅"
        return f"{status} {self.profissional} - {self.data} - {self.horas_trabalhadas}h"