from django.contrib import admin
from .models import Matricula, TipoEvento, EventoEscala, PerfilUsuario, Tipo, TPD, LegislacaoTPD, EscalaMensal, DiaEscala, ControleSemanal, MapeamentoTurno
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
    search_fields = ('profissional__nome_exibicao', 'profissional__matricula')
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

@admin.register(TPD)
class TPDAdmin(admin.ModelAdmin):
    list_display = ['profissional', 'data', 'horas_trabalhadas', 'violacao_regra']
    list_filter = ['violacao_regra', 'data']
    search_fields = ['profissional__nome_exibicao']

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-data')

@admin.register(LegislacaoTPD)
class LegislacaoTPDAdmin(admin.ModelAdmin):
    list_display = ['nome']

@admin.register(EscalaMensal)
class EscalaMensalAdmin(admin.ModelAdmin):
    list_display = ('get_mes_display', 'ano', 'hospital', 'setor', 'criado_em')
    list_filter = ('ano', 'mes', 'hospital', 'setor')

@admin.register(DiaEscala)
class DiaEscalaAdmin(admin.ModelAdmin):
    list_display = ('data', 'profissional', 'turnos', 'horas_dia')
    list_filter = ('data', 'escala')

@admin.register(ControleSemanal)
class ControleSemanalAdmin(admin.ModelAdmin):
    list_display = ('profissional', 'semana_numero', 'horas_realizadas', 'saldo_semanal')
    list_filter = ('escala', 'semana_numero')

@admin.register(MapeamentoTurno)
class MapeamentoTurnoAdmin(admin.ModelAdmin):
    list_display = ('sigla_excel', 'tipo_evento')
