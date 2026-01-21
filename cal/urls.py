from django.urls import path
from django.contrib.auth import views as auth_views
from .views import views_cal, views_dashboard, views_user, geral_views, periodo_views, especialidade_views
app_name = 'cal'


urlpatterns = [
    path('', views_user.home, name='home'),
    path('calendar/', views_cal.CalendarioView.as_view(), name='calendar'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('perfil/', views_user.perfil_usuario, name='perfil'),
    path('usuarios/', views_user.listar_usuarios, name='listar_usuarios'),
    path('usuarios/adicionar/', views_user.adicionar_usuario, name='adicionar_usuario'),
    path('usuarios/editar/<int:user_id>/', views_user.editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<int:user_id>/', views_user.excluir_usuario, name='excluir_usuario'),
    path('usuarios/resetar-senha/<int:user_id>/', views_user.resetar_senha, name='resetar_senha'),
    path('usuarios/desativar/<int:user_id>/', views_user.desativar_usuario, name='desativar_usuario'),
    path('dashboard/', views_dashboard.dashboard, name='dashboard'),
    path('plantao/novo/', views_cal.PlantaoCreateView.as_view(), name='event_new'),
    path('plantao/<int:pk>/editar/', views_cal.PlantaoUpdateView.as_view(), name='event_edit'),
    path('plantao/<int:pk>/excluir/', views_cal.PlantaoDeleteView.as_view(), name='plantao_delete'),
    path('eventos/', views_cal.MeusPlantoesListView.as_view(), name='listar_eventos'),
    path('eventos/excluir/<int:event_id>/', views_cal.excluir_evento, name='excluir_evento'),
    
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
    
    # Matrículas
    path('matriculas/', geral_views.MatriculaListView.as_view(), name='matricula_list'),
    path('matriculas/novo/', geral_views.MatriculaCreateView.as_view(), name='matricula_create'),
    path('matriculas/<int:pk>/editar/', geral_views.MatriculaUpdateView.as_view(), name='matricula_update'),
    path('matriculas/<int:pk>/excluir/', geral_views.MatriculaDeleteView.as_view(), name='matricula_delete'),

    # Tipos de Evento
    path('tipo-evento/', geral_views.TipoEventoListView.as_view(), name='tipo_evento_list'),
    path('tipo-evento/novo/', geral_views.TipoEventoCreateView.as_view(), name='tipo_evento_create'),
    path('tipo-evento/<int:pk>/editar/', geral_views.TipoEventoUpdateView.as_view(), name='tipo_evento_update'),
    path('tipo-evento/<int:pk>/excluir/', geral_views.TipoEventoDeleteView.as_view(), name='tipo_evento_delete'),

    # Períodos
    path('periodos/', periodo_views.periodo_list, name='periodo_list'),
    path('periodos/novo/', periodo_views.periodo_create, name='periodo_create'),
    path('periodos/<int:pk>/editar/', periodo_views.periodo_update, name='periodo_update'),
    path('periodos/<int:pk>/excluir/', periodo_views.periodo_delete, name='periodo_delete'),

    # Especialidades
    path('especialidades/', especialidade_views.especialidade_list, name='especialidade_list'),
    path('especialidades/novo/', especialidade_views.especialidade_create, name='especialidade_create'),
    path('especialidades/<int:pk>/editar/', especialidade_views.especialidade_update, name='especialidade_update'),
    path('especialidades/<int:pk>/excluir/', especialidade_views.especialidade_delete, name='especialidade_delete'),
]
