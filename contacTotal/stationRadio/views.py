from django.shortcuts import render
from .models import *
from .views import *

def IndexView(request):
    return render(request, "index.html")

def revista(request):
    return render(request, 'revista.html')

def programas(request):
    return render(request, 'programas.html')