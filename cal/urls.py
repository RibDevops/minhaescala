from django.urls import path
from .views import views_cal, views_dashboard, views_user, geral_views, matricula_views, tpd_views, escala_views, escala_mes_views

app_name = 'cal'

urlpatterns = [
    path('', views_user.home, name='home'),
    path('calendar/', views_cal.CalendarioView.as_view(), name='calendar'),
    path('login/', views_user.login_view, name='login'),
    path('logout/', views_user.logout_view, name='logout'),
    path('register/', views_user.register_view, name='register'),
    path('perfil/', views_user.perfil_usuario, name='perfil'),
    path('usuarios/', views_user.listar_usuarios, name='listar_usuarios'),
    path('dashboard/', views_dashboard.dashboard, name='dashboard'),
    path('plantao/novo/', views_cal.PlantaoCreateView.as_view(), name='event_new'),
    path('plantao/<int:pk>/editar/', views_cal.PlantaoUpdateView.as_view(), name='event_edit'),
    path('plantao/<int:pk>/excluir/', views_cal.PlantaoDeleteView.as_view(), name='plantao_delete'),
    path('eventos/', views_cal.MeusPlantoesListView.as_view(), name='listar_eventos'),
    path('eventos/excluir/<int:event_id>/', views_cal.excluir_evento, name='excluir_evento'),
    path('api/validar-carga/', views_cal.validar_carga_horaria, name='validar_carga_horaria'),
    
    # Tipos
    path('tipos/', geral_views.TipoListView.as_view(), name='tipo_list'),
    path('tipos/novo/', geral_views.TipoCreateView.as_view(), name='tipo_create'),
    path('tipos/<int:pk>/editar/', geral_views.TipoUpdateView.as_view(), name='tipo_update'),
    path('tipos/<int:pk>/excluir/', geral_views.TipoDeleteView.as_view(), name='tipo_delete'),

    # Tipos de Evento
    path('tipos-evento/', geral_views.TipoEventoListView.as_view(), name='tipoevento_list'),
    path('tipos-evento/novo/', geral_views.TipoEventoCreateView.as_view(), name='tipoevento_create'),
    path('tipos-evento/<int:pk>/editar/', geral_views.TipoEventoUpdateView.as_view(), name='tipoevento_update'),
    path('tipos-evento/<int:pk>/excluir/', geral_views.TipoEventoDeleteView.as_view(), name='tipoevento_delete'),

    # Hospitais
    path('hospitais/', geral_views.HospitalListView.as_view(), name='hospital_list'),
    path('hospitais/novo/', geral_views.HospitalCreateView.as_view(), name='hospital_create'),
    path('hospitais/<int:pk>/editar/', geral_views.HospitalUpdateView.as_view(), name='hospital_update'),
    path('hospitais/<int:pk>/excluir/', geral_views.HospitalDeleteView.as_view(), name='hospital_delete'),
    
    # Setores
    path('setores/', geral_views.SetorListView.as_view(), name='setor_list'),
    path('setores/novo/', geral_views.SetorCreateView.as_view(), name='setor_create'),
    path('setores/<int:pk>/editar/', geral_views.SetorUpdateView.as_view(), name='setor_update'),
    path('setores/<int:pk>/excluir/', geral_views.SetorDeleteView.as_view(), name='setor_delete'),
    
    # Especialidades
    path('especialidades/', geral_views.EspecialidadeListView.as_view(), name='especialidade_list'),
    path('especialidades/novo/', geral_views.EspecialidadeCreateView.as_view(), name='especialidade_create'),
    path('especialidades/<int:pk>/editar/', geral_views.EspecialidadeUpdateView.as_view(), name='especialidade_update'),
    path('especialidades/<int:pk>/excluir/', geral_views.EspecialidadeDeleteView.as_view(), name='especialidade_delete'),

    # Matrículas
    path('matriculas/', matricula_views.matricula_list, name='matricula_list'),
    path('matriculas/novo/', matricula_views.matricula_create, name='matricula_create'),
    path('matriculas/<int:pk>/', matricula_views.matricula_detail, name='matricula_detail'),
    path('matriculas/<int:pk>/editar/', matricula_views.matricula_update, name='matricula_update'),
    path('matriculas/<int:pk>/excluir/', matricula_views.matricula_delete, name='matricula_delete'),
    path('matriculas/<int:pk>/toggle-status/', matricula_views.matricula_toggle_status, name='matricula_toggle_status'),

    # TPD
    path('tpd/novo/', tpd_views.novo_tpd, name='novo_tpd'),
    path('tpd/listar/', tpd_views.listar_tpd, name='listar_tpd'),
    path('tpd/<int:pk>/excluir/', tpd_views.excluir_tpd, name='excluir_tpd'),
    path('tpd/relatorio/', tpd_views.relatorio_mensal, name='relatorio'),

    # Escalas
    path('escalas/', escala_views.lista_escalas, name='lista_escalas'),
    path('escalas/importar/', escala_views.importar_escala, name='importar_escala'),
    path('escalas/<int:escala_id>/', escala_views.detalhes_escala, name='escala_detalhes'),
    path('escalas/<int:escala_id>/relatorio/', escala_views.relatorio_semanal, name='escala_relatorio_semanal'),
    path('escalas/<int:escala_id>/exportar/', escala_views.exportar_escala, name='exportar_escala'),
    path('escalas/dashboard/', escala_views.dashboard_escala, name='dashboard_escala'),

        # API
    path('api/saldo-semanal/<int:profissional_id>/<int:mes>/<int:ano>/', 
             escala_views.api_saldo_semanal, name='api_saldo_semanal'),

    # Escala Mensal
    path('escala-mensal/', escala_mes_views.escala_mes_view, name='escala_mensal'),
    path('escala-mensal/<int:mes>/<int:ano>/', escala_mes_views.escala_mes_view, name='escala_mensal_mes_ano'),
    path('escala-mensal/importar/', escala_mes_views.importar_escala_excel, name='importar_escala_excel'),
    path('escala-mensal/nova/', escala_mes_views.escala_create, name='escala_create'),
    path('escala-mensal/exportar-pdf/<int:mes>/<int:ano>/', escala_mes_views.exportar_escala_pdf, name='exportar_escala_pdf'),
    path('escala-mensal/toggle-dia/<int:profissional_id>/<int:dia>/<int:mes>/<int:ano>/', escala_mes_views.toggle_dia_escala, name='toggle_dia_escala'),
]