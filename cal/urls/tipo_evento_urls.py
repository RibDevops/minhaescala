# escalas/urls/tipo_evento_urls.py
from django.urls import path
from ..views.tipo_evento_views import *

urlpatterns = [
    path('', tipo_evento_list, name='tipo_evento_list'),
    path('novo/', tipo_evento_create, name='tipo_evento_create'),
    path('<int:pk>/editar/', tipo_evento_update, name='tipo_evento_update'),
    path('<int:pk>/excluir/', tipo_evento_delete, name='tipo_evento_delete'),
]