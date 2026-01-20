from django.contrib import admin
from .models import Hospital, Setor, Periodo, TipoEvento, PerfilUsuario, Matricula, EventoEscala, Especialidade

@admin.register(EventoEscala)
class EventoEscalaAdmin(admin.ModelAdmin):
    list_display = ('data', 'get_profissional', 'tipo_evento', 'setor', 'hospital')
    list_filter = ('hospital', 'setor', 'tipo_evento', 'data')
    search_fields = ('profissional__nome_exibicao', 'profissional__numero')
    date_hierarchy = 'data'
    
    def get_profissional(self, obj):
        return obj.profissional.nome_exibicao
    get_profissional.short_description = 'Profissional'

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nome_exibicao', 'carga_horaria_semanal')
    filter_horizontal = ('hospitais', 'setores', 'especialidades')
    search_fields = ('numero', 'nome_exibicao', 'nome_completo')

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla')
    search_fields = ('nome', 'sigla')

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'hospital')
    list_filter = ('hospital',)
    search_fields = ('nome',)

@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'periodo', 'horas', 'contabiliza_carga_horaria')
    list_filter = ('periodo', 'contabiliza_carga_horaria')
    search_fields = ('nome', 'codigo')

admin.site.register(Periodo)
admin.site.register(PerfilUsuario)
admin.site.register(Especialidade)
