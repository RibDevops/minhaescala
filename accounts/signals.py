from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario
from core.models import Hospital


@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        hospital_padrao = Hospital.objects.first()
        PerfilUsuario.objects.create(
            user=instance,
            hospital=hospital_padrao
        )
