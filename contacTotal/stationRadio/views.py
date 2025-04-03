from django.shortcuts import render
from .models import *
from .views import *

def IndexView(request):
    return render(request, "index.html")

def revista(request):
    return render(request, 'revista.html')

def programas(request):
    return render(request, 'programas.html')

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
