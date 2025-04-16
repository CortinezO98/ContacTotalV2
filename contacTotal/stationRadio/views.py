from django.shortcuts import render, get_object_or_404
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMessage, BadHeaderError
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.conf.urls.static import static
import smtplib
import urllib.parse


def IndexView(request):
    latest_edicion = EdicionRevista.objects.all().order_by('-fecha_publicacion', '-id').first()
    main_video = MainVideo.objects.first()
    anuncios = Anuncio.objects.all()
    carousel_news_qs = CarouselNews.objects.all().order_by('-publication_date')[:6]
    carousel_news_list = list(carousel_news_qs)
    carousel_news = [carousel_news_list[i:i+3] for i in range(0, len(carousel_news_list), 3)]
    main_news = MainNews.objects.all().order_by('-publication_date').first()
    last_podcasts = PodcastSection.objects.order_by('-date_created')[:6]
    last_programs = Programa.objects.order_by('-fecha_creacion', '-id')[:3]
    
    # Banners verticales
    banners_left = Banner.objects.filter(activo=True, position='vertical_left').order_by('orden')
    banners_right = Banner.objects.filter(activo=True, position='vertical_right').order_by('orden')
    
    # Banners horizontales por posición
    banner_horizontal_after_carousel = Banner.objects.filter(activo=True, position='horizontal_after_carousel').order_by('orden')
    banner_horizontal_after_main_news = Banner.objects.filter(activo=True, position='horizontal_after_main_news').order_by('orden')
    banner_horizontal_after_podcast = Banner.objects.filter(activo=True, position='horizontal_after_podcast').order_by('orden')
    banner_horizontal_after_programs = Banner.objects.filter(activo=True, position='horizontal_after_programs').order_by('orden')
    
    context = {
        'latest_edicion': latest_edicion,
        'main_video': main_video,
        'anuncios': anuncios,
        'carousel_news': carousel_news,
        'main_news': main_news,
        'last_podcasts': last_podcasts,
        'last_programs': last_programs,
        'banners_left': banners_left,
        'banners_right': banners_right,
        'banner_horizontal_after_carousel': banner_horizontal_after_carousel,
        'banner_horizontal_after_main_news': banner_horizontal_after_main_news,
        'banner_horizontal_after_podcast': banner_horizontal_after_podcast,
        'banner_horizontal_after_programs': banner_horizontal_after_programs,
    }
    return render(request, "index.html", context)


def noticia_detalle(request, slug):

    news_item = MainNews.objects.filter(slug=slug).first() or get_object_or_404(CarouselNews, slug=slug)

    left_ads = Announcement.objects.filter(active=True, position='left')[:2]
    right_ads = Announcement.objects.filter(active=True, position='right')[:2]
    inline_ads = Announcement.objects.filter(active=True, position='inline')[:1]
    bottom_ads = Announcement.objects.filter(active=True, position='bottom')[:1]

    context = {
        'news_item': news_item,
        'left_ads': left_ads,
        'right_ads': right_ads,
        'inline_ads': inline_ads,
        'bottom_ads': bottom_ads,
        'logo_type': 'noticia',  
    }

    return render(request, 'noticia_detalle.html', context)


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
    
    left_ads  = Announcement.objects.filter(active=True, position='left')[:2]
    right_ads = Announcement.objects.filter(active=True, position='right')[:2]
    
    context = {
        'page_obj': page_obj,
        'left_ads': left_ads,
        'right_ads': right_ads,
        'logo_type': 'revista'
    }
    
    return render(request, 'revista.html', context)





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
    
    left_ads  = Announcement.objects.filter(active=True, position='left')[:2]
    right_ads = Announcement.objects.filter(active=True, position='right')[:2]
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'left_ads': left_ads,
        'right_ads': right_ads,
        'logo_type': 'programas'
    }
    return render(request, 'programas.html', context)


def podcast(request):
    featured_section = PodcastSection.objects.filter(featured=True).first()
    if featured_section:
        sections = PodcastSection.objects.exclude(id=featured_section.id).order_by('-date_created')
    else:
        sections = PodcastSection.objects.all().order_by('-date_created')
    
    left_ads  = Announcement.objects.filter(active=True, position='left')[:2]
    right_ads = Announcement.objects.filter(active=True, position='right')[:2]

    context = {
        'featured_section': featured_section,
        'sections': sections,
        'left_ads': left_ads,
        'right_ads': right_ads,
        'logo_type': 'podcast'
    }
    return render(request, 'podcast.html', context)


def podcast_detail(request, slug):
    section = get_object_or_404(PodcastSection, slug=slug)
    audios = section.audios.all().order_by('-date_created')
    videos = section.videos.all().order_by('-date_created')

    context = {
        'section': section,
        'audios': audios,
        'videos': videos,
    }
    return render(request, 'podcast_detail.html', context)





def quienesSomos(request):
    left_ads  = Announcement.objects.filter(active=True, position='left')[:2]
    right_ads = Announcement.objects.filter(active=True, position='right')[:2]

    context = {
        'left_ads': left_ads,
        'right_ads': right_ads,
        'logo_type': 'quienes_somos'
    }
    return render(request, 'quienesSomos.html', context)


def programacion(request):
    programacion_list = Programacion.objects.all()
    left_ads  = Announcement.objects.filter(active=True, position='left')[:2]
    right_ads = Announcement.objects.filter(active=True, position='right')[:2]

    for item in programacion_list:
        item.hora_bogota = item.get_otra_zona_horaria('America/Bogota')  
        item.hora_mexico = item.get_otra_zona_horaria('America/Mexico_City')  
        item.hora_argentina = item.get_otra_zona_horaria('America/Argentina/Buenos_Aires')  
        item.hora_eeuu = item.get_otra_zona_horaria('America/New_York') 

    context = {
        'programacion': programacion_list,
        'left_ads': left_ads,
        'right_ads': right_ads,
        'logo_type': 'programacion'
    }
    return render(request, 'programacion.html', context)



def contacto(request):
    left_ads  = Announcement.objects.filter(active=True, position='left')[:2]
    right_ads = Announcement.objects.filter(active=True, position='right')[:2]


    context = {
        'left_ads':  left_ads,
        'right_ads': right_ads,
        'logo_type': 'contacto',
    }

    status = request.GET.get('status')
    msg    = request.GET.get('msg')
    if status:
        context.update({
            'status':    status,
            'swal_title': "Éxito" if status == "success" else "Error",
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
                to=['jcortinezosorio@gmail.com'],
                headers={'Reply-To': 'no-reply@revistacontactototal.com'}
            )
            email_message.content_subtype = 'html'
            email_message.send(fail_silently=False)

            success_msg = urllib.parse.quote("Tu mensaje fue enviado con éxito.")
            return HttpResponseRedirect(f"{reverse('contacto')}?status=success&msg={success_msg}")

        except (BadHeaderError, smtplib.SMTPException, Exception) as e:
            err_msg = urllib.parse.quote(f"Error al enviar el mensaje: {str(e)}")
            return HttpResponseRedirect(f"{reverse('contacto')}?status=error&msg={err_msg}")

    return render(request, 'contacto.html', context)


def anunciate(request):
    left_ads  = Announcement.objects.filter(active=True, position='left')[:2]
    right_ads = Announcement.objects.filter(active=True, position='right')[:2]

    context = {
        'left_ads': left_ads,
        'right_ads': right_ads,
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
                to=['jcortinezosorio@gmail.com'],
                headers={'Reply-To': 'no-reply@contactototalmedia.com'}
            )
            email_message.content_subtype = 'html'
            email_message.send(fail_silently=False)

            context.update({
                'status': 'success',
                'swal_title': 'Éxito',
                'msg': 'Tu solicitud fue enviada con éxito.'
            })

        except (BadHeaderError, smtplib.SMTPException, Exception) as e:
            context.update({
                'status': 'error',
                'swal_title': 'Error',
                'msg': f'Error al enviar el mensaje: {str(e)}'
            })

    return render(request, 'anunciate.html', context)

