from django.urls import path, re_path
from . import views

app_name = 'cal'

urlpatterns = [
    path('index/', views.index, name='index'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('event/new/', views.event, name='event_new'),
    path('eventos/', views.listar_eventos, name='listar_eventos'),
    path('eventos/excluir/<int:event_id>/', views.excluir_evento, name='excluir_evento'),

    re_path(r'^event/edit/(?P<event_id>\d+)/$', views.event, name='event_edit'),
]
