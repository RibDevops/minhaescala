# escalas/urls/hospital_urls.py
from django.urls import path
from ..views.hospital_views import *

urlpatterns = [
    path('', hospital_list, name='hospital_list'),
    path('novo/', hospital_create, name='hospital_create'),
    path('<int:pk>/', hospital_detail, name='hospital_detail'),
    path('<int:pk>/editar/', hospital_update, name='hospital_update'),
    path('<int:pk>/excluir/', hospital_delete, name='hospital_delete'),
]