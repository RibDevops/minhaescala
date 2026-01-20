# escalas/urls/setor_urls.py
from django.urls import path
from ..views.setor_views import *

urlpatterns = [
    path('', setor_list, name='setor_list'),
    path('novo/', setor_create, name='setor_create'),
    path('<int:pk>/editar/', setor_update, name='setor_update'),
    path('<int:pk>/excluir/', setor_delete, name='setor_delete'),
]