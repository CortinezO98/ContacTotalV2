from django.db import models
from pytz import timezone
import pytz
from datetime import datetime
from django.utils.text import slugify


# Podcast
class Podcast(models.Model):
    PODCAST_TYPE_CHOICES = (
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('mixed', 'Mixto'), 
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='podcasts_covers/', blank=True, null=True)
    audio_file = models.FileField(upload_to='podcasts_audio/', blank=True, null=True)
    video_link = models.URLField(blank=True, null=True, help_text="Enlace para el video (embed de YouTube, por ejemplo)")
    podcast_type = models.CharField(max_length=10, choices=PODCAST_TYPE_CHOICES, default='audio')
    date_created = models.DateField(auto_now_add=True)
    featured = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True, editable=False)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title





# ANUNCIO REUTILIZABLE EN VISTAS
class Announcement(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    link = models.URLField(blank=True, null=True, help_text="Link a donde redirige el anuncio")
    date_created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title or f"Anuncio {self.id}"



# Revistas
class EdicionRevista(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='revistas/')
    fecha_publicacion = models.DateField(auto_now_add=True)
    url = models.URLField()

    def __str__(self):
        return self.titulo
    

# Video principal del header
class MainVideo(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, help_text="Título opcional para el video")
    video_file = models.FileField(upload_to='videos/', blank=True, null=True, help_text="Sube un archivo de video (mp4 recomendado)")
    video_link = models.URLField(blank=True, null=True, help_text="O ingresa un link al video (por ejemplo, URL de YouTube embed)")

    def video_source(self):
        """
        Devuelve la fuente del video:
        - Si se subió un archivo, devuelve su URL.
        - Si no, pero se ingresó un link, devuelve el link.
        - En caso contrario, devuelve None.
        """
        if self.video_file:
            return self.video_file.url
        elif self.video_link:
            return self.video_link
        return None

    def __str__(self):
        return self.title or "Main Video"


# Carrusel de Noticias (Index)
class CarouselNews(models.Model):
    title = models.CharField(max_length=255)
    publication_date = models.DateField()
    author = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='carousel_news/')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# Noticia Principal (Index)
class MainNews(models.Model):
    title = models.CharField(max_length=255)
    video = models.FileField(upload_to='main_news/videos/', blank=True, null=True, help_text="Sube un video (formato mp4 recomendado)")
    video_link = models.URLField(blank=True, null=True, help_text="O ingresa un link al video (por ejemplo, YouTube embed)")
    image = models.ImageField(upload_to='main_news/images/', blank=True, null=True, help_text="Usa esta imagen si no se proporciona un video")
    author = models.CharField(max_length=255)
    publication_date = models.DateField()
    short_description = models.TextField(help_text="Descripción corta de la noticia")
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def media_source(self):
        """
        Devuelve la fuente del medio:
        - Si se subió un video, se devuelve la URL del archivo.
        - De lo contrario, si se proporcionó un enlace, se devuelve el enlace.
        - Si no hay video, se usa la imagen.
        """
        if self.video:
            return self.video.url
        elif self.video_link:
            return self.video_link
        elif self.image:
            return self.image.url
        return None

    def __str__(self):
        return self.title

# Anuncios
class Anuncio(models.Model):
    imagen = models.ImageField(upload_to='anuncios/')
    titulo = models.CharField(max_length=255, blank=True, null=True, help_text="Opcional: Título o descripción breve del anuncio.")

    def __str__(self):
        return self.titulo or "Anuncio"


# Vista Programa
class Programa(models.Model):
    titulo = models.CharField(max_length=200)
    host = models.CharField(max_length=200)
    duracion = models.DecimalField(max_digits=5, decimal_places=2)  
    url_reproducir = models.URLField()  

    def __str__(self):
        return self.titulo


# Vista Programacion
class Programacion(models.Model):
    dia = models.DateField()  
    programa = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='programacion_imagenes/')
    hora = models.TimeField()  # Hora almacenada como TimeField
    zona_horaria_usuario = models.CharField(
        max_length=50,
        choices=[('America/Mexico_City', 'Mexico'),
                ('America/Bogota', 'Bogota'),
                ('America/Argentina/Buenos_Aires', 'Argentina'),
                ('America/New_York', 'EEUU')]
    )

    def get_otra_zona_horaria(self, zona_horaria_destino):
        """Convierte la hora de la zona horaria del usuario a otra zona horaria."""
        user_tz = timezone(self.zona_horaria_usuario)

        user_time = self.hora

        localized_time = user_tz.localize(datetime.combine(datetime.today(), user_time))

        target_tz = timezone(zona_horaria_destino)
        converted_time = localized_time.astimezone(target_tz)

        return converted_time.strftime('%H:%M:%S')

    @property
    def dia_semana(self):
        """Devuelve el día de la semana en formato textual, como 'Lunes', 'Martes', etc."""
        return self.dia.strftime('%A')

    def __str__(self):
        return f'{self.dia_semana} - {self.programa}'