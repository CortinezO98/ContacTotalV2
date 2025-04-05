from django.shortcuts import render, get_object_or_404
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def IndexView(request):
    latest_edicion = EdicionRevista.objects.all().order_by('-fecha_publicacion', '-id').first()
    main_video = MainVideo.objects.first()
    anuncios = Anuncio.objects.all()
    carousel_news_qs = CarouselNews.objects.all().order_by('-publication_date')[:6]
    carousel_news_list = list(carousel_news_qs)
    carousel_news = [carousel_news_list[i:i+3] for i in range(0, len(carousel_news_list), 3)]
    main_news = MainNews.objects.all().order_by('-publication_date').first()
    last_podcasts = Podcast.objects.order_by('-date_created')[:6]
    last_programs = Programa.objects.order_by('-fecha_creacion', '-id')[:6]
    
    context = {
        'latest_edicion': latest_edicion,
        'main_video': main_video,
        'anuncios': anuncios,
        'carousel_news': carousel_news,
        'main_news': main_news,
        'last_podcasts': last_podcasts,
        'last_programs': last_programs,
    }
    return render(request, "index.html", context)


def noticia_detalle(request, slug):
    news_item = MainNews.objects.filter(slug=slug).first() or get_object_or_404(CarouselNews, slug=slug)
    return render(request, 'noticia_detalle.html', {'news_item': news_item})


def revista(request):
    ediciones_list = EdicionRevista.objects.all().order_by('-fecha_publicacion', '-id')
    paginator = Paginator(ediciones_list, 12)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    
    left_ads = Announcement.objects.filter(active=True)[:2]
    right_ads = Announcement.objects.filter(active=True)[2:4]
    
    context = {
        'page_obj': page_obj,
        'left_ads': left_ads,
        'right_ads': right_ads,
    }
    
    return render(request, 'revista.html', {'page_obj': page_obj})




def programas(request):
    query = request.GET.get('q', '')
    if query:
        programas_list = Programa.objects.filter(titulo__icontains=query).order_by('-id')
    else:
        programas_list = Programa.objects.all().order_by('-id')
    
    paginator = Paginator(programas_list, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    
    left_ads = Announcement.objects.filter(active=True)[:2]
    right_ads = Announcement.objects.filter(active=True)[2:4]
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'left_ads': left_ads,
        'right_ads': right_ads,
    }
    return render(request, 'programas.html', context)


def podcast(request):
    featured_podcast = Podcast.objects.filter(featured=True).first()
    if not featured_podcast:
        featured_podcast = Podcast.objects.order_by('-date_created').first()
    if featured_podcast:
        podcasts = Podcast.objects.exclude(id=featured_podcast.id).order_by('-date_created')
    else:
        podcasts = Podcast.objects.order_by('-date_created')
    
    left_ads = Announcement.objects.filter(active=True)[:2]
    right_ads = Announcement.objects.filter(active=True)[2:4]

    context = {
        'featured_podcast': featured_podcast,
        'podcasts': podcasts,
        'left_ads': left_ads,
        'right_ads': right_ads,
    }
    return render(request, 'podcast.html', context)


def podcast_detail(request, slug):
    podcast = get_object_or_404(Podcast, slug=slug)
    return render(request, 'podcast_detail.html', {'podcast': podcast})





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
