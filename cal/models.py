from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Hospital(models.Model):
    nome_hospital = models.CharField(max_length=200)
    sigla = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitais"
        ordering = ['nome_hospital']
    
    def __str__(self):
        return f"{self.nome_hospital} ({self.sigla})" if self.sigla else self.nome_hospital

class Setor(models.Model):
    TIPO_SETOR_CHOICES = [
        ('UTI', 'Unidade de Terapia Intensiva'),
        ('CTI', 'Centro de Terapia Intensiva'),
        ('PS', 'Pronto Socorro'),
        ('CO', 'Centro Obstétrico'),
        ('CC', 'Centro Cirúrgico'),
        ('ENF', 'Enfermaria'),
        ('AMB', 'Ambulatório'),
        ('ADM', 'Administrativo'),
        ('OUT', 'Outro'),
    ]
    
    nome_setor = models.CharField(max_length=200)
    sigla = models.CharField(max_length=20, blank=True, null=True)
    tipo_setor = models.CharField(max_length=10, choices=TIPO_SETOR_CHOICES, default='ENF')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='setores')
    capacidade = models.IntegerField(default=0, help_text="Quantidade máxima de profissionais por turno")
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"
        ordering = ['hospital', 'nome_setor']
        unique_together = ['nome_setor', 'hospital']
    
    def __str__(self):
        return f"{self.nome_setor} - {self.hospital.sigla}"

class TipoPlantao(models.Model):
    TIPO_CHOICES = [
        ('NORMAL', 'Normal'),
        ('TPD', 'TPD'),
        ('TPD+', 'TPD Extra'),
        ('EXTRA', 'Extra'),
        ('PLANTAO', 'Plantão'),
        ('SOBREAVISO', 'Sobreaviso'),
    ]
    
    STATUS_CHOICES = [
        ('FOLGA', 'Folga'),
        ('FERIAS', 'Férias'),
        ('LICMAT', 'Licença Maternidade'),
        ('LICPRE', 'Licença Prêmio'),
        ('LICSAU', 'Licença Saúde'),
        ('ABONO', 'Abono'),
        ('AUSENC', 'Ausência'),
        ('DISPEN', 'Dispensa'),
        ('OUTROS', 'Outros'),
    ]
    
    PERIODO_CHOICES = [
        ('SM', 'Manhã (06:00-12:00)'),
        ('ST', 'Tarde (12:00-18:00)'),
        ('SN', 'Noite (18:00-06:00)'),
        ('SD', 'Dia (06:00-18:00)'),
        ('24H', '24 Horas'),
        ('SF', 'Folga'),
    ]
    
    codigo = models.CharField(max_length=10, unique=True, help_text="Código único do tipo (ex: FOL, FER, TPD)")
    descricao = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
    periodo = models.CharField(max_length=3, choices=PERIODO_CHOICES)
    horas = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(24)])
    paga_extra = models.BooleanField(default=False, help_text="Se gera horas extras")
    gera_banco_horas = models.BooleanField(default=True, help_text="Se contabiliza para banco de horas")
    cor = models.CharField(max_length=7, default='#3498db', help_text="Cor no calendário (hex)")
    ordem = models.IntegerField(default=0, help_text="Ordem de exibição")
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Tipo de Plantão"
        verbose_name_plural = "Tipos de Plantão"
        ordering = ['ordem', 'descricao']
    
    def __str__(self):
        return f"{self.codigo} - {self.descricao} ({self.horas}h)"

class PerfilUsuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('PROFISSIONAL', 'Profissional'),
        ('ESCALANTE', 'Escalante'),
        ('CHEFE', 'Chefe de Setor'),
        ('ADMIN', 'Administrador'),
        ('RH', 'Recursos Humanos'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='PROFISSIONAL')
    cpf = models.CharField(max_length=14, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    data_admissao = models.DateField(default=timezone.now)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    ativo = models.BooleanField(default=True)
    
    # Permissões específicas
    pode_escalar = models.BooleanField(default=False)
    pode_aprovar = models.BooleanField(default=False)
    pode_visualizar_todos = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuário"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_tipo_usuario_display()}"

class Enfermeiro(models.Model):
    perfil = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE, related_name='enfermeiro')
    nome = models.CharField(max_length=255, related_name='Nome do Enfermeiro')
    nome_completo = models.CharField(max_length=255, related_name='Nome Completo do Enfermeiro')
    matricula = models.CharField(max_length=50, unique=True)
    coren = models.CharField(max_length=20, blank=True, null=True, help_text="Registro no COREN")
    
    # Dados profissionais
    especialidade = models.CharField(max_length=100, blank=True, null=True)
    nivel = models.CharField(max_length=50, blank=True, null=True, help_text="Nível profissional (ex: Enf. I, Enf. II)")
    carga_horaria_mensal = models.IntegerField(
        default=180,
        validators=[MinValueValidator(0), MaxValueValidator(300)],
        help_text="Carga horária contratual mensal em horas"
    )
    
    # Vinculação
    hospitais = models.ManyToManyField(Hospital, related_name='enfermeiros')
    setores = models.ManyToManyField(Setor, related_name='enfermeiros')
    setor_principal = models.ForeignKey(
        Setor, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='enfermeiros_principal'
    )
    
    # Status
    ativo = models.BooleanField(default=True)
    em_ferias = models.BooleanField(default=False)
    data_inicio_ferias = models.DateField(blank=True, null=True)
    data_fim_ferias = models.DateField(blank=True, null=True)
    
    # Informações de contato emergência
    contato_emergencia = models.CharField(max_length=255, blank=True, null=True)
    telefone_emergencia = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        verbose_name = "Enfermeiro"
        verbose_name_plural = "Enfermeiros"
        ordering = ['nome_completo']
    
    def __str__(self):
        return f"{self.nome_completo} ({self.matricula})"
    
    @property
    def usuario(self):
        return self.perfil.user
    
    @property
    def esta_disponivel(self):
        """Verifica se o enfermeiro está disponível para escala"""
        if not self.ativo:
            return False
        if self.em_ferias:
            hoje = timezone.now().date()
            if self.data_inicio_ferias and self.data_fim_ferias:
                return not (self.data_inicio_ferias <= hoje <= self.data_fim_ferias)
        return True

class ControleHoras(models.Model):
    enfermeiro = models.ForeignKey(Enfermeiro, on_delete=models.CASCADE, related_name='controle_horas')
    mes_referencia = models.DateField(help_text="Mês de referência (primeiro dia do mês)")
    
    # Controle de horas
    horas_previstas = models.IntegerField(default=0, help_text="Horas previstas no mês")
    horas_realizadas = models.IntegerField(default=0, help_text="Horas trabalhadas no mês")
    horas_extras = models.IntegerField(default=0, help_text="Horas extras realizadas")
    horas_faltas = models.IntegerField(default=0, help_text="Horas faltantes/debito")
    
    # Banco de horas
    saldo_anterior = models.IntegerField(
        default=0,
        verbose_name="CG. ANT.",
        help_text="Carga horária acumulada do mês anterior"
    )
    saldo_atual = models.IntegerField(
        default=0,
        verbose_name="CG. ATUAL",
        help_text="Saldo atual do mês (calculado)"
    )
    
    # Controle de pagamento
    horas_pagar = models.IntegerField(default=0, help_text="Horas para pagamento em dinheiro")
    horas_banco = models.IntegerField(default=0, help_text="Horas para banco de horas")
    
    # Status
    fechado = models.BooleanField(default=False, help_text="Se o mês foi fechado/finalizado")
    data_fechamento = models.DateField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Controle de Horas"
        verbose_name_plural = "Controles de Horas"
        ordering = ['-mes_referencia']
        unique_together = ['enfermeiro', 'mes_referencia']
    
    def __str__(self):
        return f"Controle {self.mes_referencia.strftime('%m/%Y')} - {self.enfermeiro.nome_completo}"
    
    def calcular_saldo(self):
        """Calcula o saldo atual baseado nas horas realizadas"""
        saldo_bruto = self.saldo_anterior + (self.horas_realizadas - self.horas_previstas)
        self.saldo_atual = saldo_bruto
        return self.saldo_atual
    
    def fechar_mes(self):
        """Fecha o mês atual e prepara para o próximo"""
        if not self.fechado:
            self.calcular_saldo()
            self.fechado = True
            self.data_fechamento = timezone.now().date()
            self.save()
            
            # Cria registro para o próximo mês
            proximo_mes = self.mes_referencia.replace(month=self.mes_referencia.month + 1)
            if self.mes_referencia.month == 12:
                proximo_mes = self.mes_referencia.replace(year=self.mes_referencia.year + 1, month=1)
            
            ControleHoras.objects.create(
                enfermeiro=self.enfermeiro,
                mes_referencia=proximo_mes,
                saldo_anterior=self.saldo_atual,
                horas_previstas=self.enfermeiro.carga_horaria_mensal
            )

class Escala(models.Model):
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('PUBLICADA', 'Publicada'),
        ('APROVADA', 'Aprovada'),
        ('EM_EXECUCAO', 'Em Execução'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    mes_referencia = models.DateField(help_text="Mês de referência (primeiro dia do mês)")
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, related_name='escalas')
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='escalas_criadas')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RASCUNHO')
    
    # Datas importantes
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_publicacao = models.DateTimeField(blank=True, null=True)
    data_aprovacao = models.DateTimeField(blank=True, null=True)
    
    # Metadados
    observacoes = models.TextField(blank=True, null=True)
    arquivo_pdf = models.FileField(upload_to='escalas_pdf/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Escala"
        verbose_name_plural = "Escalas"
        ordering = ['-mes_referencia']
        unique_together = ['mes_referencia', 'setor']
    
    def __str__(self):
        return f"Escala {self.setor} - {self.mes_referencia.strftime('%m/%Y')}"
    
    @property
    def mes_ano(self):
        return self.mes_referencia.strftime('%B/%Y').title()

class Plantao(models.Model):
    escala = models.ForeignKey(Escala, on_delete=models.CASCADE, related_name='plantoes')
    enfermeiro = models.ForeignKey(Enfermeiro, on_delete=models.CASCADE, related_name='plantoes')
    tipo_plantao = models.ForeignKey(TipoPlantao, on_delete=models.PROTECT)
    
    # Data e horário
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    
    # Informações adicionais
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, related_name='plantoes')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='plantoes')
    
    # Status
    realizado = models.BooleanField(default=False)
    confirmado = models.BooleanField(default=False)
    substituicao = models.BooleanField(default=False)
    
    # Substituição (se aplicável)
    substituido_por = models.ForeignKey(
        Enfermeiro, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='plantoes_substituidos'
    )
    
    # Observações
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Plantão"
        verbose_name_plural = "Plantões"
        ordering = ['data', 'hora_inicio']
        indexes = [
            models.Index(fields=['data', 'enfermeiro']),
            models.Index(fields=['escala', 'data']),
        ]
    
    def __str__(self):
        return f"{self.enfermeiro.nome_completo} - {self.data.strftime('%d/%m/%Y')} - {self.tipo_plantao.codigo}"
    
    @property
    def horas_trabalhadas(self):
        """Calcula horas trabalhadas baseado no tipo de plantão ou horário"""
        if self.tipo_plantao and self.tipo_plantao.horas > 0:
            return self.tipo_plantao.horas
        
        # Se não tiver tipo definido, calcula pela diferença de horários
        from datetime import datetime
        if self.hora_inicio and self.hora_fim:
            inicio = datetime.combine(self.data, self.hora_inicio)
            fim = datetime.combine(self.data, self.hora_fim)
            # Ajusta para o próximo dia se necessário
            if fim < inicio:
                fim = datetime.combine(self.data.replace(day=self.data.day + 1), self.hora_fim)
            diff = fim - inicio
            return diff.total_seconds() / 3600
        return 0
    
    def pode_substituir(self, novo_enfermeiro):
        """Verifica se pode ser substituído por outro enfermeiro"""
        # Regras de substituição
        if not novo_enfermeiro.ativo:
            return False, "Enfermeiro inativo"
        if not novo_enfermeiro.esta_disponivel:
            return False, "Enfermeiro não disponível"
        if novo_enfermeiro.hospitais.filter(id=self.hospital.id).exists():
            return True, "Substituição permitida"
        return False, "Enfermeiro não pertence ao hospital"

class Solicitacao(models.Model):
    TIPO_SOLICITACAO_CHOICES = [
        ('TROCA', 'Troca de Plantão'),
        ('FOLGA', 'Solicitação de Folga'),
        ('FERIAS', 'Agendamento de Férias'),
        ('LICENCA', 'Licença'),
        ('ABONO', 'Abono'),
        ('OUTROS', 'Outros'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADA', 'Aprovada'),
        ('REJEITADA', 'Rejeitada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    enfermeiro = models.ForeignKey(Enfermeiro, on_delete=models.CASCADE, related_name='solicitacoes')
    tipo = models.CharField(max_length=20, choices=TIPO_SOLICITACAO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    
    # Datas
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)
    
    # Plantões envolvidos (para trocas)
    plantao_origem = models.ForeignKey(
        Plantao, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='solicitacoes_troca'
    )
    plantao_destino = models.ForeignKey(
        Plantao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitacoes_recebidas'
    )
    enfermeiro_destino = models.ForeignKey(
        Enfermeiro,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitacoes_recebidas'
    )
    
    # Aprovação
    aprovado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    
    # Detalhes
    motivo = models.TextField()
    justificativa_aprovacao = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Solicitação"
        verbose_name_plural = "Solicitações"
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"Solicitação {self.get_tipo_display()} - {self.enfermeiro.nome_completo}"