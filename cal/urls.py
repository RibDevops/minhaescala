from django.urls import path
from . import views

app_name = 'cal'

urlpatterns = [
    path('', views.CalendarioView.as_view(), name='calendar'),
    path('calendar/', views.CalendarioView.as_view(), name='calendar_full'),
    path('plantao/novo/', views.PlantaoCreateView.as_view(), name='event_new'),
    path('plantao/<int:pk>/editar/', views.PlantaoUpdateView.as_view(), name='event_edit'),
    path('plantao/<int:pk>/excluir/', views.PlantaoDeleteView.as_view(), name='plantao_delete'),
    path('eventos/', views.MeusPlantoesListView.as_view(), name='listar_eventos'),
    path('eventos/excluir/<int:event_id>/', views.excluir_evento, name='excluir_evento'),
]
