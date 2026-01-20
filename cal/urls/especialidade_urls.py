# escalas/urls/especialidade_urls.py
from django.urls import path
from ..views.especialidade_views import *

urlpatterns = [
    path('', especialidade_list, name='especialidade_list'),
    path('novo/', especialidade_create, name='especialidade_create'),
    path('<int:pk>/editar/', especialidade_update, name='especialidade_update'),
    path('<int:pk>/excluir/', especialidade_delete, name='especialidade_delete'),
]