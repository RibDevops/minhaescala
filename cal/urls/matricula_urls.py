# escalas/urls/matricula_urls.py
from django.urls import path
from ..views.matricula_views import *

urlpatterns = [
    path('', matricula_list, name='matricula_list'),
    path('novo/', matricula_create, name='matricula_create'),
    path('<int:pk>/', matricula_detail, name='matricula_detail'),
    path('<int:pk>/editar/', matricula_update, name='matricula_update'),
    path('<int:pk>/excluir/', matricula_delete, name='matricula_delete'),
]