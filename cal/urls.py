from django.urls import path
from . import views

app_name = 'cal'

urlpatterns = [
    path('', views.home, name='home'),
    path('calendar/', views.CalendarioView.as_view(), name='calendar'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/adicionar/', views.adicionar_usuario, name='adicionar_usuario'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<int:user_id>/', views.excluir_usuario, name='excluir_usuario'),
    path('usuarios/resetar-senha/<int:user_id>/', views.resetar_senha, name='resetar_senha'),
    path('usuarios/desativar/<int:user_id>/', views.desativar_usuario, name='desativar_usuario'),
    path('password-reset/', views.login_view, name='password_reset'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('plantao/novo/', views.PlantaoCreateView.as_view(), name='event_new'),
    path('plantao/<int:pk>/editar/', views.PlantaoUpdateView.as_view(), name='event_edit'),
    path('plantao/<int:pk>/excluir/', views.PlantaoDeleteView.as_view(), name='plantao_delete'),
    path('eventos/', views.MeusPlantoesListView.as_view(), name='listar_eventos'),
    path('eventos/excluir/<int:event_id>/', views.excluir_evento, name='excluir_evento'),
]

# urls_solicitacoes.py - Adicionar ao urls.py principal
from django.urls import path
from . import views_solicitacoes

urlpatterns += [
    path('solicitacoes/nova/', views_solicitacoes.SolicitacaoCreateView.as_view(), name='solicitacao_create'),
    path('solicitacoes/minhas/', views_solicitacoes.MinhasSolicitacoesListView.as_view(), name='minhas_solicitacoes'),
    path('solicitacoes/<int:pk>/aprovar/', views_solicitacoes.SolicitacaoAprovarView.as_view(), name='aprovar_solicitacao'),
    path('solicitacoes/pendentes/', views_solicitacoes.SolicitacoesPendentesListView.as_view(), name='solicitacoes_pendentes'),
]