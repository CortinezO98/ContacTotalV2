from django.shortcuts import render
from .models import *
from .views import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def IndexView(request):
    return render(request, "index.html")

def revista(request):
    ediciones = EdicionRevista.objects.all().order_by('-fecha_publicacion') 
    return render(request, 'revista.html', {'ediciones': ediciones})


def programas(request):
    programas_list = Programa.objects.all()  
    paginator = Paginator(programas_list, 10) 

    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)  

    return render(request, 'programas.html', {'page_obj': page_obj})

def podcast(request):
    featured_podcast = Podcast.objects.filter(featured=True).first()
    if not featured_podcast:
        featured_podcast = Podcast.objects.order_by('-date_created').first()
    if featured_podcast is not None:
        podcasts = Podcast.objects.exclude(id=featured_podcast.id).order_by('-date_created')
    else:
        podcasts = []  

    context = {
        'featured_podcast': featured_podcast,
        'podcasts': podcasts
    }
    return render(request, 'podcast.html', context)


def radio(request):
    return render(request, 'radio.html')


def quienesSomos(request):
    return render(request, 'quienesSomos.html')

def programacion(request):
    programacion_list = Programacion.objects.all()

    for item in programacion_list:
        item.hora_bogota = item.get_otra_zona_horaria('America/Bogota')  
        item.hora_mexico = item.get_otra_zona_horaria('America/Mexico_City')  
        item.hora_argentina = item.get_otra_zona_horaria('America/Argentina/Buenos_Aires')  
        item.hora_eeuu = item.get_otra_zona_horaria('America/New_York') 

    context = {
        'programacion': programacion_list,
    }
    return render(request, 'programacion.html', context)


def tienda(request):
    return render(request, 'tienda.html')

def contacto(request):
    return render(request, 'contacto.html')

def noticias(request):
    return render(request, 'noticias.html')
