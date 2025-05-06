from django.shortcuts import render

from .views import *

# def home(request, year, month):
def home(request):
    return render(request, 'home.html', {})