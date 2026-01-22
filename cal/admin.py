from django.contrib import admin
from .models import Matricula, TipoEvento, EventoEscala, PerfilUsuario, Tipo
from core.models import Hospital, Setor

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('user__username', 'user__email')

@admin.register(EventoEscala)
class EventoEscalaAdmin(admin.ModelAdmin):
    list_display = ('data', 'get_profissional', 'tipo', 'setor', 'hospital')
    list_filter = ('hospital', 'setor', 'tipo', 'data')
    search_fields = ('profissional__nome_guerra', 'profissional__matricula')
    date_hierarchy = 'data'
    
    def get_profissional(self, obj):
        return obj.profissional.nome_exibicao
    get_profissional.short_description = 'Profissional'

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'nome_exibicao', 'hospital', 'setor', 'especialidade', 'carga_horaria_semanal', 'ativo')
    list_filter = ('hospital', 'setor', 'especialidade', 'ativo')
    search_fields = ('matricula', 'nome_exibicao', 'nome_completo')

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla')
    search_fields = ('nome', 'sigla')

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'hospital')
    list_filter = ('hospital',)
    search_fields = ('nome',)

@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'tipo_descricao', 'contabiliza')
    list_filter = ('contabiliza',)
    search_fields = ('tipo', 'tipo_descricao')

@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao', 'horas', 'tipo_base')
    list_filter = ('tipo_base',)
    search_fields = ('descricao', 'codigo')
