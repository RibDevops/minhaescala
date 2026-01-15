from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Hospital(models.Model):
    nome_hospital = models.CharField(max_length=200)
    def __str__(self):
        return self.nome_hospital

class Setor(models.Model):
    nome_setor = models.CharField(max_length=200)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='setores')
    def __str__(self):
        return f"{self.nome_setor} ({self.hospital.nome_hospital})"

class TipoPlantao(models.Model):
    TIPO_CHOICES = [('Normal', 'Normal'), ('TPD', 'TPD')]
    PERIODO_CHOICES = [('SM', 'Manhã'), ('ST', 'Tarde'), ('SN', 'Noite')]
    HORAS_CHOICES = [(6, '6h'), (12, '12h')]
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    periodo = models.CharField(max_length=2, choices=PERIODO_CHOICES)
    qtd_horas = models.IntegerField(choices=HORAS_CHOICES)
    
    def __str__(self):
        return f"{self.tipo} - {self.get_periodo_display()} ({self.qtd_horas}h)"

class Enfermeiro(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nome_completo = models.CharField(max_length=255)
    matricula = models.CharField(max_length=50) # Pode ser extendido para múltiplas se necessário
    hospitais = models.ManyToManyField(Hospital)
    setores = models.ManyToManyField(Setor)
    carga_horaria = models.IntegerField(help_text="Carga horária mensal")
    
    def __str__(self):
        return self.nome_completo

class Event(models.Model):
    enfermeiro = models.ForeignKey(Enfermeiro, on_delete=models.CASCADE, related_name='eventos', null=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True)
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True)
    tipo_plantao = models.ForeignKey(TipoPlantao, on_delete=models.SET_NULL, null=True)
    
    title = models.CharField(max_length=200, verbose_name="Título do Evento")
    start_time = models.DateField(verbose_name="Data", null=True, blank=True)

    @property
    def get_html_url(self):
        url = reverse('cal:event_edit', args=(self.id,))
        return f'<a href="{url}" class="event">{self.title}</a>'
