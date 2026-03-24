from django.contrib import admin
from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'hospital', 'ativo')
    list_filter = ('tipo', 'hospital', 'ativo')
    search_fields = ('user__username', 'user__email')
