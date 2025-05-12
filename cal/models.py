from django.db import models
from django.urls import reverse

class Event(models.Model):
    title = models.CharField(max_length=200)
    # description = models.TextField()
    # start_time = models.DateTimeField()
    # end_time = models.DateTimeField()
    start_time = models.DateField(
        verbose_name="Data de início",
        # auto_now_add=False,  # Define como data atual apenas na criação
        null=True,           # Permite valores nulos
        blank=True           # Permite campo em branco no formulário
    )
    end_time = models.DateField(
        verbose_name="Data de início",
        # auto_now_add=False,  # Define como data atual apenas na criação
        null=True,           # Permite valores nulos
        blank=True           # Permite campo em branco no formulário
    )

    # start_time = models.DateField()  # Armazena apenas data
    # end_time = models.DateField()    # Armazena apenas data

    @property
    def get_html_url(self):
        url = reverse('cal:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'
