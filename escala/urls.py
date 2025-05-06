import os
from django.urls import path
from escala import views

app_name = 'escala'

urlpatterns = [
    path('', views.home, name='home'),
    # path('<int:year>/<str:month>', views.home, name='home'),

]
