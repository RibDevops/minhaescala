from django.contrib import admin
from .models import Hospital, Setor, Periodo, TipoEvento, PerfilUsuario, Matricula, EventoEscala

@admin.register(EventoEscala)
class EventoEscalaAdmin(admin.ModelAdmin):
    list_display = ('data', 'profissional_nome', 'tipo_evento', 'setor', 'hospital')
    list_filter = ('hospital', 'setor', 'tipo_evento', 'data')
    search_fields = ('profissional__nome_exibicao', 'profissional__numero')
    date_hierarchy = 'data'
    
    def profissional_nome(self, obj):
        return obj.profissional.nome_exibicao
    profissional_nome.short_description = 'Profissional'

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nome_exibicao', 'carga_horaria_semanal')
    filter_horizontal = ('hospitais', 'setores')

admin.site.register(Hospital)
admin.site.register(Setor)
admin.site.register(Periodo)
admin.site.register(TipoEvento)
admin.site.register(PerfilUsuario)
