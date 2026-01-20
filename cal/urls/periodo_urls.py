# escalas/urls/periodo_urls.py
from django.urls import path
from ..views.periodo_views import *

urlpatterns = [
    path('', periodo_list, name='periodo_list'),
    path('novo/', periodo_create, name='periodo_create'),
    path('<int:pk>/editar/', periodo_update, name='periodo_update'),
    path('<int:pk>/excluir/', periodo_delete, name='periodo_delete'),
]