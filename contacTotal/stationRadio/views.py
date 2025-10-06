from django.shortcuts import render, get_object_or_404
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from urllib.parse import urlencode
from django.core.mail import EmailMessage, BadHeaderError
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.conf.urls.static import static
import smtplib
import urllib.parse
from datetime import datetime, time
from math import ceil
import pytz
from stationRadio.utils.announcements import get_announcements
from itertools import chain



def IndexView(request):
    main_video = MainVideo.objects.first()
    anuncios = Anuncio.objects.all()
    carousel_news_qs = CarouselNews.objects.all().order_by('-publication_date')[:6]
    carousel_news_list = list(carousel_news_qs)
    carousel_news = [carousel_news_list[i:i+3] for i in range(0, len(carousel_news_list), 3)]
    main_news = MainNews.objects.all().order_by('-publication_date').first()
    last_podcasts = PodcastSection.objects.order_by('-date_created')[:6]
    last_programs = Programa.objects.order_by('-fecha_creacion', '-id')[:3]
    latest_podcast_section = PodcastSection.objects.order_by('-date_created', '-id').first()
    noticias_flat = list(CarouselNews.objects.all().order_by('-publication_date')[:6])
    podcasts_flat = list(PodcastSection.objects.order_by('-date_created')[:6])
    banners_left = Banner.objects.filter(activo=True, position='vertical_left').order_by('orden')
    banners_right = Banner.objects.filter(activo=True, position='vertical_right').order_by('orden')

    def _banner_key(b):
        if b.script:
            return f"script:{hash(b.script)}"
        for field in ('image_desktop', 'image_tablet', 'image_mobile'):
            img = getattr(b, field, None)
            if img and getattr(img, 'name', ''):
                return f"img:{img.name}"
        return f"id:{b.pk}"

    banners_mobile = []
    _seen = set()
    for b in chain(banners_left, banners_right):
        k = _banner_key(b)
        if k not in _seen:
            _seen.add(k)
            banners_mobile.append(b)

    banner_horizontal_after_carousel = Banner.objects.filter(activo=True, position='horizontal_after_carousel').order_by('orden')
    banner_horizontal_after_main_news = Banner.objects.filter(activo=True, position='horizontal_after_main_news').order_by('orden')
    banner_horizontal_after_podcast = Banner.objects.filter(activo=True, position='horizontal_after_podcast').order_by('orden')
    banner_horizontal_after_programs = Banner.objects.filter(activo=True, position='horizontal_after_programs').order_by('orden')

    if latest_podcast_section:
        latest_audio = PodcastAudio.objects.filter(
            podcast_section=latest_podcast_section
        ).order_by('-date_created', '-id').first()
    else:
        latest_audio = None


    now = datetime.now(pytz.timezone('America/Phoenix'))
    current_time = now.time()
    now = datetime.now(pytz.timezone('America/Phoenix'))
    current_day = now.weekday()
    current_time = now.time()

    twitch_schedule = TwitchSchedule.objects.filter(
        day_of_week=current_day,
        start_time__lte=current_time,
        end_time__gt=current_time,
        is_active=True
    ).first()

    next_start_schedule = TwitchSchedule.objects.filter(
        day_of_week=current_day,
        start_time__gt=current_time,
        is_active=True
    ).order_by('start_time').first()

    next_end_schedule = TwitchSchedule.objects.filter(
        day_of_week=current_day,
        end_time__gt=current_time,
        is_active=True
    ).order_by('end_time').first()
    
    show_twitch = twitch_schedule is not None or main_video is None
    twitch_channel = twitch_schedule.twitch_channel if twitch_schedule else 'contactototalmedia'

    current_ms = (current_time.hour * 3600 + current_time.minute * 60 + current_time.second) * 1000
    next_change_ms = None

    if next_start_schedule:
        next_start_ms = (next_start_schedule.start_time.hour * 3600 + 
                         next_start_schedule.start_time.minute * 60 + 
                         next_start_schedule.start_time.second) * 1000
        if next_end_schedule:
            next_end_ms = (next_end_schedule.end_time.hour * 3600 + 
                           next_end_schedule.end_time.minute * 60 + 
                           next_end_schedule.end_time.second) * 1000
            next_change_ms = min(next_start_ms, next_end_ms)
        else:
            next_change_ms = next_start_ms
    elif next_end_schedule:
        next_change_ms = (next_end_schedule.end_time.hour * 3600 + 
                          next_end_schedule.end_time.minute * 60 + 
                          next_end_schedule.end_time.second) * 1000
    
    context = {
        'main_video': main_video,
        'anuncios': anuncios,
        'carousel_news': carousel_news,
        'main_news': main_news,
        'last_podcasts': last_podcasts,
        'last_programs': last_programs,
        'latest_podcast_section': latest_podcast_section,
        'latest_audio': latest_audio,
        'noticias_flat': noticias_flat,
        'podcasts_flat': podcasts_flat,
        'banners_left': banners_left,
        'banners_right': banners_right,
        'banners_mobile': banners_mobile,  
        'banner_horizontal_after_carousel': banner_horizontal_after_carousel,
        'banner_horizontal_after_main_news': banner_horizontal_after_main_news,
        'banner_horizontal_after_podcast': banner_horizontal_after_podcast,
        'banner_horizontal_after_programs': banner_horizontal_after_programs,
        'show_twitch': show_twitch,
        'twitch_channel': twitch_channel,
        'current_ms': current_ms,
        'next_change_ms': next_change_ms,
    }
    return render(request, "index.html", context)


def noticia_detalle(request, slug):

    news_item = MainNews.objects.filter(slug=slug).first() or get_object_or_404(CarouselNews, slug=slug)

    left_ads   = get_announcements('left',   'noticia_detalle', 2)
    right_ads  = get_announcements('right',  'noticia_detalle', 2)
    inline_ads = get_announcements('inline', 'noticia_detalle', 1)
    bottom_ads = get_announcements('bottom', 'noticia_detalle', 1)
    mobile_top_ads    = get_announcements('inline', 'noticia_detalle', 2)
    mobile_bottom_ads = get_announcements('bottom', 'noticia_detalle', 2)

    context = {
        'news_item': news_item,
        'left_ads': left_ads, 'right_ads': right_ads,
        'inline_ads': inline_ads, 'bottom_ads': bottom_ads,
        'mobile_top_ads': mobile_top_ads,
        'mobile_bottom_ads': mobile_bottom_ads,        
        'logo_type': 'noticia',  
    }

    return render(request, 'noticia_detalle.html', context)




#REVISTA
def revista(request):
    ediciones_list = (EdicionRevista.objects.filter(status='published').order_by('-fecha_publicacion', '-id'))
    paginator = Paginator(ediciones_list, 12)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    elided_range = paginator.get_elided_page_range(
        number=page_obj.number, on_each_side=1, on_ends=1
    )
    qs = request.GET.copy()
    qs.pop('page', None)
    preserved_query = urlencode(qs, doseq=True)

    left_ads  = get_announcements('left',  'revista', 2)
    right_ads = get_announcements('right', 'revista', 2)
    mobile_top_ads    = get_announcements('inline', 'revista', 2)
    mobile_bottom_ads = get_announcements('bottom', 'revista', 2)

    context = {
        'page_obj': page_obj,
        'elided_range': elided_range,         
        'preserved_query': preserved_query,    
        'left_ads': left_ads, 'right_ads': right_ads,
        'mobile_top_ads': mobile_top_ads,
        'mobile_bottom_ads': mobile_bottom_ads,
        'logo_type': 'revista'
    }
    return render(request, 'revista.html', context)


#DETALLE REVISTA
def revista_detail(request, slug):
    """Detalle de una edición con su artículo principal y secundarios"""
    edicion = get_object_or_404(EdicionRevista, slug=slug, status='published')
    if edicion.is_pdf_only():
        return redirect(edicion.pdf.url)

    articulos   = edicion.articulos.filter(status='published')
    principal   = articulos.filter(es_principal=True).first()
    secundarios = articulos.filter(es_principal=False)


    left_ads   = get_announcements('left',   'revista_detail', 2)
    right_ads  = get_announcements('right',  'revista_detail', 2)
    inline_ads = get_announcements('inline', 'revista_detail', 3)
    mobile_top_ads    = get_announcements('inline', 'revista_detail', 2)
    mobile_bottom_ads = get_announcements('bottom', 'revista_detail', 2)



    context = {
        'edicion':     edicion,
        'principal':   principal,
        'secundarios': secundarios,
        'left_ads': left_ads, 'right_ads': right_ads, 'inline_ads': inline_ads,
        'mobile_top_ads': mobile_top_ads,
        'mobile_bottom_ads': mobile_bottom_ads,
        'logo_type':   'revistaa',
    }

    return render(request, 'revista_detail.html',context)

#ARTICULO
def articulo_detail(request, slug):
    articulo = get_object_or_404(Articulo,slug=slug,status='published',edicion__status='published')
    parrafos = articulo.contenido.split('\n\n') 
    imagenes = list(articulo.imagenes.all().order_by('orden'))
    contenido_mezclado = []
    max_len = max(len(parrafos), len(imagenes))

    for i in range(max_len):
        if i < len(parrafos):
            contenido_mezclado.append({'tipo': 'parrafo', 'contenido': parrafos[i].strip()})
        if i < len(imagenes):
            contenido_mezclado.append({'tipo': 'imagen', 'contenido': imagenes[i]})

    left_ads   = get_announcements('left',   'articulo_detail', 2)
    right_ads  = get_announcements('right',  'articulo_detail', 2)
    inline_ads = get_announcements('inline', 'articulo_detail', 1)
    mobile_top_ads    = get_announcements('inline', 'articulo_detail', 2)
    mobile_bottom_ads = get_announcements('bottom', 'articulo_detail', 2)


    context = {
        'articulo': articulo,
        'contenido_mezclado': contenido_mezclado,
        'left_ads': left_ads, 'right_ads': right_ads, 'inline_ads': inline_ads,
        'mobile_top_ads': mobile_top_ads,
        'mobile_bottom_ads': mobile_bottom_ads,
        'logo_type': 'revistaa',
    }

    return render(request, 'articulo_detail.html', context)






#PROGRAMAS/RADIO

def programas(request):
    query = (request.GET.get('q') or '').strip()
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
    
    left_ads  = get_announcements('left',  'programas', 2)
    right_ads = get_announcements('right', 'programas', 2)
    mobile_top_ads    = get_announcements('inline', 'programas', 2)
    mobile_bottom_ads = get_announcements('bottom', 'programas', 2)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'left_ads': left_ads, 'right_ads': right_ads,
        'mobile_top_ads': mobile_top_ads,
        'mobile_bottom_ads': mobile_bottom_ads,
        'logo_type': 'programas'
    }
    return render(request, 'programas.html', context)

# PODCAST
def podcast(request):
    featured_section = PodcastSection.objects.filter(featured=True).first()
    if featured_section:
        sections = PodcastSection.objects.exclude(id=featured_section.id).order_by('-date_created')
    else:
        sections = PodcastSection.objects.all().order_by('-date_created')
    
    left_ads   = get_announcements('left',   'podcast', 2)
    right_ads  = get_announcements('right',  'podcast', 2)
    bottom_ads = get_announcements('bottom', 'podcast', 1)
    mobile_top_ads    = get_announcements('inline', 'podcast', 2)
    mobile_bottom_ads = get_announcements('bottom', 'podcast', 2)
    context = {
        'featured_section': featured_section,
        'sections': sections,
        'left_ads': left_ads, 'right_ads': right_ads, 'bottom_ads': bottom_ads,
        'mobile_top_ads': mobile_top_ads,
        'mobile_bottom_ads': mobile_bottom_ads,
        'logo_type': 'podcast'
    }
    return render(request, 'podcast.html', context)

# PODCAST DETALLE
def podcast_detail(request, slug):
    section = get_object_or_404(PodcastSection, slug=slug)
    all_audios = section.audios.order_by('-date_created')
    all_videos = section.videos.order_by('-date_created')
    paginator_audio = Paginator(all_audios, 12)
    page_audio = request.GET.get('audio_page', 1)
    try:
        audios = paginator_audio.page(page_audio)
    except (PageNotAnInteger, EmptyPage):
        audios = paginator_audio.page(1)
        
    paginator_video = Paginator(all_videos, 12)
    page_video = request.GET.get('video_page', 1)
    try:
        videos = paginator_video.page(page_video)
    except (PageNotAnInteger, EmptyPage):
        videos = paginator_video.page(1)

    left_ads   = get_announcements('left',   'podcast_detail', 2)
    right_ads  = get_announcements('right',  'podcast_detail', 2)
    inline_ads = get_announcements('inline', 'podcast_detail', 1)
    bottom_ads = get_announcements('bottom', 'podcast_detail', 1)
    mobile_top_ads    = get_announcements('inline', 'podcast_detail', 2)
    mobile_bottom_ads = get_announcements('bottom', 'podcast_detail', 2)

    context = {
        'section':       section,
        'audios':        audios,
        'videos':        videos,
        'audio_page':    audios.number,
        'video_page':    videos.number,
        'left_ads': left_ads, 'right_ads': right_ads,
        'inline_ads': inline_ads, 'bottom_ads': bottom_ads,
        'mobile_top_ads': mobile_top_ads,
        'mobile_bottom_ads': mobile_bottom_ads,
        'logo_type': 'podcastsDetalle'
    }
    return render(request, 'podcast_detail.html', context)




#QUIENES SOMOS
def quienesSomos(request):
    left_ads  = get_announcements('left',  'quienesSomos', 2)
    right_ads = get_announcements('right', 'quienesSomos', 2)
    mobile_top_ads    = get_announcements('inline', 'quienesSomos', 2)
    mobile_bottom_ads = get_announcements('bottom', 'quienesSomos', 2)

    context = {
        'left_ads': left_ads, 'right_ads': right_ads,
        'mobile_top_ads': mobile_top_ads,
        'mobile_bottom_ads': mobile_bottom_ads,
        'logo_type': 'quienes_somos'
    }
    return render(request, 'quienesSomos.html', context)

# PROGRAMACION


START_HOUR   = 8         
END_HOUR     = 22         
SLOT_MINUTES = 30      

PY_WEEKDAY_TO_KEY = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}

def programacion(request):
    """
    Parrilla semanal (08:00–22:00) con CSS Grid (30 min por fila).
    - Sin posiciones absolutas para eventos.
    - Carriles por día con grid-column (no hay solapamientos).
    """
    base_tz = getattr(request, 'user_timezone', None) or settings.TIME_ZONE
    base_tz_label = base_tz.split('/')[-1].replace('_', ' ')

    min_start = START_HOUR * 60
    max_end   = END_HOUR   * 60
    total_minutes = max_end - min_start
    rows = total_minutes // SLOT_MINUTES 

    def to_minutes(hhmm: str) -> int:
        h, m = hhmm.split(':')
        return int(h) * 60 + int(m)

    day_labels = dict(DAYS_OF_WEEK)
    day_order  = [k for k, _ in DAYS_OF_WEEK]
    events_by_day = {k: [] for k in day_order}
    for p in Programacion.objects.all():
        start_local = p.get_otra_zona_horaria(base_tz, p.hora_inicio)  # 'HH:MM'
        end_local   = p.get_otra_zona_horaria(base_tz, p.hora_fin)

        s = to_minutes(start_local)
        e = to_minutes(end_local)
        if e <= s: 
            e += 24 * 60

        vs = max(s, min_start)
        ve = min(e, max_end)
        if ve <= vs:
            continue

        base_ev = {
            'title': p.programa,
            'image_url': p.imagen.url if p.imagen else None,
            'start_label': start_local,
            'end_label': end_local,
            's': vs, 'e': ve,
        }
        for d in p.dias_semana:
            if d in events_by_day:
                events_by_day[d].append(dict(base_ev))

    columns = []
    for k in day_order:
        events = events_by_day[k]
        events.sort(key=lambda ev: (ev['s'], ev['e']))
        clusters, cur, cur_end = [], [], -1
        for ev in events:
            if not cur:
                cur = [ev]; cur_end = ev['e']
            elif ev['s'] < cur_end:  
                cur.append(ev); cur_end = max(cur_end, ev['e'])
            else:
                clusters.append(cur); cur = [ev]; cur_end = ev['e']
        if cur: clusters.append(cur)

        max_lanes = 1
        for cluster in clusters:
            lanes = []  
            for ev in cluster:
                placed = False
                for i, lane_end in enumerate(lanes):
                    if ev['s'] >= lane_end:
                        lanes[i] = ev['e']
                        ev['lane'] = i
                        placed = True
                        break
                if not placed:
                    ev['lane'] = len(lanes)
                    lanes.append(ev['e'])
                row_start = (ev['s'] - min_start) // SLOT_MINUTES + 1
                row_end   = int(ceil((ev['e'] - min_start) / SLOT_MINUTES)) + 1
                if row_end <= row_start:
                    row_end = row_start + 1  

                ev['row_start'] = max(1, row_start)
                ev['row_end']   = min(rows + 1, row_end)

            max_lanes = max(max_lanes, len(lanes))

        columns.append({
            'key': k,
            'label': day_labels[k],
            'events': events,
            'lanes': max(1, max_lanes),  
        })
    now = datetime.now(pytz.timezone(base_tz))
    today_key = PY_WEEKDAY_TO_KEY[now.weekday()]
    now_min = now.hour * 60 + now.minute
    show_now_line = (min_start <= now_min <= max_end)
    now_top_pct = ((now_min - min_start) * 100.0 / total_minutes) if show_now_line else None

    hours, h = [], min_start
    while h <= max_end:
        hours.append({'label': f"{h//60:02d}:00",
                      'top_pct': (h - min_start) * 100.0 / total_minutes})
        h += 60

    for col in columns:
        col['is_today'] = (col['key'] == today_key)


    left_ads  = get_announcements('left',  'programacion', 2)
    right_ads = get_announcements('right', 'programacion', 2)
    mobile_top_ads    = get_announcements('inline', 'programacion', 2)
    mobile_bottom_ads = get_announcements('bottom', 'programacion', 2)

    context = {
        'columns': columns,
        'rows': rows,                
        'hours': hours,            
        'show_now_line': show_now_line,
        'now_top_pct': now_top_pct,
        'base_tz_label': base_tz_label,
        'left_ads': left_ads, 'right_ads': right_ads,
        'mobile_top_ads': mobile_top_ads,
        'mobile_bottom_ads': mobile_bottom_ads,
        'logo_type': 'programacion',
    }
    return render(request, 'programacion.html', context)


#CONTACTATE
def contacto(request):
    left_ads  = get_announcements('left',  'contacto', 2)
    right_ads = get_announcements('right', 'contacto', 2)
    mobile_top_ads    = get_announcements('inline', 'contacto', 2)
    mobile_bottom_ads = get_announcements('bottom', 'contacto', 2)


    context = {
        'left_ads': left_ads, 'right_ads': right_ads,
        'mobile_top_ads': mobile_top_ads,
        'mobile_bottom_ads': mobile_bottom_ads,
        'logo_type': 'contacto',
    }

    status = request.GET.get('status')
    msg    = request.GET.get('msg')
    if status:
        context.update({
            'status':    status,
            'swal_title': "¡Muchas gracias por contactarnos!" if status == "success" else "Error",
            'msg':        urllib.parse.unquote(msg) if msg else "",
        })

    if request.method == 'POST':
        nombre  = request.POST.get('nombre', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email    = request.POST.get('email', '').strip()
        mensaje  = request.POST.get('mensaje', '').strip()


        context.update({
            'nombre':  nombre,
            'telefono': telefono,
            'email':    email,
            'mensaje':  mensaje,
        })

        if not nombre or not telefono or not email:
            error_msg = urllib.parse.quote("Por favor completa todos los campos obligatorios.")
            return HttpResponseRedirect(f"{reverse('contacto')}?status=error&msg={error_msg}")

        ContactMessage.objects.create(
            nombre=nombre,
            telefono=telefono,
            email=email,
            mensaje=mensaje
        )

        html_contenido = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 30px;
                    background-color: #ffffff; border: 1px solid #ddd; border-radius: 10px;">
            <div style="text-align: center;">
                <img src="https://contactototalmedia.com/img/Logo%20CT%20Media%20PNG.png"
                    alt="Logo Contacto Total" style="max-width: 150px; margin-bottom: 20px;">
                <h2 style="color: #ff0000; margin-bottom: 5px;">📬 Mensaje de Contacto</h2>
                <p style="margin-top: 0; color: #ff0000;">Revista Contacto Total</p>
                <hr style="margin: 20px 0;">
            </div>
            <h4 style="color: #333;">📌 Detalles del remitente</h4>
            <table style="width: 100%; font-size: 15px;">
                <tr><td><strong>👤 Nombre:</strong></td><td>{nombre}</td></tr>
                <tr><td><strong>📞 Teléfono:</strong></td><td>{telefono}</td></tr>
                <tr><td><strong>📧 Correo:</strong></td><td>{email}</td></tr>
            </table>
            <hr style="margin: 20px 0;">
            <h4 style="color: #333;">📝 Mensaje</h4>
            <p style="font-size: 15px; line-height: 1.6; color: #444;">
                {mensaje or "Sin mensaje adicional."}
            </p>
            <hr style="margin: 30px 0;">
            <p style="font-size: 12px; color: #888; text-align: center;">
                Este mensaje fue enviado desde el formulario de contacto de Revista Contacto Total.
            </p>
        </div>
        """

        try:
            email_message = EmailMessage(
                subject='📬 Contacto desde Revista Contacto Total',
                body=html_contenido,
                from_email=settings.EMAIL_HOST_USER,
                to=['contactenos@contactototalmedia.com'],
                headers={'Reply-To': 'no-reply@contactenos.com'}
            )
            email_message.content_subtype = 'html'
            email_message.send(fail_silently=False)

            success_msg = urllib.parse.quote("Hemos recibido tu mensaje y te responderemos lo más pronto posible. Si necesitas asistencia de manera urgente, por favor comunícate al 602-751-2106.")
            return HttpResponseRedirect(f"{reverse('contacto')}?status=success&msg={success_msg}")

        except (BadHeaderError, smtplib.SMTPException, Exception) as e:
            err_msg = urllib.parse.quote(f"Error al enviar el mensaje: {str(e)}")
            return HttpResponseRedirect(f"{reverse('contacto')}?status=error&msg={err_msg}")

    return render(request, 'contacto.html', context)

#ANUNCIATE CON NOSTROS PARA PUBLICIDAD
def anunciate(request):
    left_ads  = get_announcements('left',  'anunciate', 2)
    right_ads = get_announcements('right', 'anunciate', 2)
    mobile_top_ads    = get_announcements('inline', 'anunciate', 2)
    mobile_bottom_ads = get_announcements('bottom', 'anunciate', 2)

    context = {
        'left_ads': left_ads, 'right_ads': right_ads,
        'mobile_top_ads': mobile_top_ads,
        'mobile_bottom_ads': mobile_bottom_ads,
        'logo_type': 'contacto'
    }

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        cargo = request.POST.get('cargo', '').strip()
        empresa = request.POST.get('empresa', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()
        comentarios = request.POST.get('comentarios', '').strip()

        context.update({
            'nombre': nombre,
            'cargo': cargo,
            'empresa': empresa,
            'telefono': telefono,
            'email': email,
            'comentarios': comentarios,
        })

        if not nombre or not cargo or not empresa or not telefono or not email:
            context.update({
                'status': 'error',
                'swal_title': 'Error',
                'msg': 'Por favor completa todos los campos obligatorios.'
            })
            return render(request, 'anunciate.html', context)

        html_contenido = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 30px; background-color: #ffffff; border: 1px solid #ddd; border-radius: 10px;">
            <div style="text-align: center;">
                <img src="https://contactototalmedia.com/img/Logo%20CT%20Media%20PNG.png" alt="Logo Contacto Total" style="max-width: 150px; margin-bottom: 20px;">
                <h2 style="color: #e60000; margin-bottom: 5px;">📢 Solicitud de Publicidad</h2>
                <p style="margin-top: 0; color: #e60000;">Contacto Total Media</p>
                <hr style="margin: 20px 0;">
            </div>
            <h4 style="color: #333;">🧾 Detalles del solicitante</h4>
            <table style="width: 100%; font-size: 15px;">
                <tr><td style="padding: 8px 0;"><strong>👤 Nombre:</strong></td><td>{nombre}</td></tr>
                <tr><td style="padding: 8px 0;"><strong>💼 Cargo:</strong></td><td>{cargo}</td></tr>
                <tr><td style="padding: 8px 0;"><strong>🏢 Empresa:</strong></td><td>{empresa}</td></tr>
                <tr><td style="padding: 8px 0;"><strong>📞 Teléfono:</strong></td><td>{telefono}</td></tr>
                <tr><td style="padding: 8px 0;"><strong>📧 Correo:</strong></td><td>{email}</td></tr>
            </table>
            <hr style="margin: 20px 0;">
            <h4 style="color: #333;">📝 Comentarios</h4>
            <p style="font-size: 15px; line-height: 1.6; color: #444;">{comentarios or "Sin comentarios adicionales."}</p>
            <hr style="margin: 30px 0;">
            <p style="font-size: 12px; color: #888; text-align: center;">
                Este mensaje fue enviado desde el formulario de publicidad de Contacto Total Media.
            </p>
        </div>
        """

        try:
            PublicidadContacto.objects.create(
                nombre=nombre,
                cargo=cargo,
                empresa=empresa,
                telefono=telefono,
                email=email,
                comentarios=comentarios
            )

            email_message = EmailMessage(
                subject='📢 Solicitud de publicidad desde Contacto Total Media',
                body=html_contenido,
                from_email=settings.EMAIL_HOST_USER,
                to=['sales@contactototalmedia.com'],
                headers={'Reply-To': 'no-reply@contactototalmedia.com'}
            )
            email_message.content_subtype = 'html'
            email_message.send(fail_silently=False)

            context.update({
                'status': 'success',
                'swal_title': '¡Muchas gracias por contactarnos!',
                'msg': 'Hemos recibido tu mensaje y te responderemos lo más pronto posible. Si necesitas asistencia de manera urgente, por favor comunícate al 602-751-2106.'
            })

        except (BadHeaderError, smtplib.SMTPException, Exception) as e:
            context.update({
                'status': 'error',
                'swal_title': 'Error',
                'msg': f'Error al enviar el mensaje: {str(e)}'
            })

    return render(request, 'anunciate.html', context)

def equipo(request):
    """Vista para mostrar el equipo de trabajo"""
    left_ads  = get_announcements('left',  'equipo', 2)
    right_ads = get_announcements('right', 'equipo', 2)
    mobile_top_ads    = get_announcements('inline', 'equipo', 2)
    mobile_bottom_ads = get_announcements('bottom', 'equipo', 2)

    context = {
        'left_ads': left_ads, 
        'right_ads': right_ads,
        'mobile_top_ads': mobile_top_ads,
        'mobile_bottom_ads': mobile_bottom_ads,
        'logo_type': 'equipo'
    }
    return render(request, 'equipo.html', context)

