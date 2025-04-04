"""
URL configuration for contacTotal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from stationRadio.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView, name="index"),
    path('revista/', revista, name="revista"),
    path('programas/', programas, name="programas"),
    path('podcast/', podcast, name="podcast"),
    path('radio/', radio, name="radio"),
    path('quienesSomos/', quienesSomos, name="quienesSomos"),
    path('programacion/', programacion, name="programacion"),
    path('tienda/', tienda, name="tienda"),
    path('contacto/', contacto, name="contacto"),
    path('noticia/<slug:slug>/', noticia_detalle, name='noticia_detalle'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
