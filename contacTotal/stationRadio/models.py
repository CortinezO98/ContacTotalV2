from django.db import models
from pytz import timezone
import pytz
from datetime import datetime
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.urls import reverse


# Podcast
class PodcastSection(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='podcasts_covers/', blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True, editable=False)
    featured = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(PodcastSection, self).save(*args, **kwargs)

    def _str_(self):
        return self.title

class PodcastAudio(models.Model):
    podcast_section = models.ForeignKey(PodcastSection, related_name='audios', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    audio_file = models.FileField(upload_to='podcasts_audio/')
    audio_link = models.URLField(blank=True, null=True, help_text="Enlace embed de YouTube, por ejemplo")
    duration = models.CharField(max_length=20, blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    

    def _str_(self):
        return self.title

class PodcastVideo(models.Model):
    podcast_section = models.ForeignKey(PodcastSection, related_name='videos', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_link = models.URLField(blank=True, null=True, help_text="Enlace embed de YouTube, por ejemplo")
    cover_image = models.ImageField(upload_to='podcasts_video_covers/', blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)

    def _str_(self):
        return self.title


# ANUNCIO REUTILIZABLE EN VISTAS
class Announcement(models.Model):
    POSITION_CHOICES = [
        ('left', 'Izquierda'),
        ('right', 'Derecha'),
        ('inline', 'Dentro del contenido'),
        ('bottom', 'Final del contenido'),
    ]

    title = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    link = models.URLField(blank=True, null=True, help_text="Link a donde redirige el anuncio")
    position = models.CharField(
        max_length=10,
        choices=POSITION_CHOICES,
        default='right',
        help_text="Ubicación del anuncio en la página"
    )
    custom_script = models.TextField(
        blank=True,
        null=True,
        help_text="Código HTML o script del anuncio (tendrá prioridad sobre la imagen si se define)"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title or f"Anuncio {self.id}"



# REVISTA Y ARTICULOS
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, editable=False)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            num = 1
            while Tag.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class EdicionRevista(TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='revistas/portadas/')
    fecha_publicacion = models.DateField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', db_index=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, editable=False)
    pdf = models.FileField(upload_to='revistas/pdf/', blank=True, null=True, help_text="Si sólo subes este PDF, no habrá detalle de artículos")

    class Meta:
        ordering = ['-fecha_publicacion', '-id']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'fecha_publicacion']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titulo)
            slug = base_slug
            num = 1
            while EdicionRevista.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def is_pdf_only(self):
        return bool(self.pdf and not self.articulos.exists())

    def get_absolute_url(self):
        if self.is_pdf_only():
            return self.pdf.url
        return reverse('revista_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.titulo

class Articulo(TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
    ]

    edicion = models.ForeignKey(EdicionRevista, related_name='articulos', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, editable=False)
    portada = models.ImageField(upload_to='revistas/articulos/')
    descripcion_corta = models.CharField(max_length=255, help_text="Resumen breve")
    contenido = models.TextField(help_text="Descripción completa")
    autor = models.CharField(max_length=100, blank=True, null=True)
    fecha_publicado = models.DateField(auto_now_add=True, db_index=True)
    es_principal = models.BooleanField(default=False, help_text="Marca este artículo como principal", db_index=True)
    orden = models.PositiveIntegerField(default=0, help_text="Orden en la lista")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', db_index=True)
    view_count = models.PositiveIntegerField(default=0, help_text="Número de vistas")
    tags = models.ManyToManyField(Tag, blank=True, related_name='articulos')
    external_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL externa relacionada con este artículo")

    class Meta:
        ordering = ['-es_principal', 'orden']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'es_principal']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['edicion'],
                condition=models.Q(es_principal=True),
                name='one_principal_per_edicion'
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titulo)
            slug = base_slug
            num = 1
            while Articulo.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('articulo_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return f"{self.titulo} ({self.edicion.titulo})"




    

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

    def _str_(self):
        return self.title or "Main Video"


# Carrusel de Noticias (Index)
class CarouselNews(models.Model):
    title = models.CharField(max_length=255)
    publication_date = models.DateField()
    author = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='carousel_news/')
    slug = models.SlugField(unique=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def _str_(self):
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

    def _str_(self):
        return self.title

# Anuncios
class Anuncio(models.Model):
    imagen = models.ImageField(upload_to='anuncios/')
    titulo = models.CharField(max_length=255, blank=True, null=True, help_text="Opcional: Título o descripción breve del anuncio.")

    def _str_(self):
        return self.titulo or "Anuncio"


class Banner(models.Model):
    POSITION_CHOICES = (
        ('vertical_left', 'Vertical Izquierdo'),
        ('vertical_right', 'Vertical Derecho'),
        ('horizontal_after_carousel', 'Horizontal - Después del Carrusel'),
        ('horizontal_after_main_news', 'Horizontal - Después de Noticias Principal'),
        ('horizontal_after_podcast', 'Horizontal - Después del Podcast'),
        ('horizontal_after_programs', 'Horizontal - Después de Programas'),
    )
    
    position = models.CharField(max_length=30,choices=POSITION_CHOICES,verbose_name="Posición")
    orden = models.PositiveIntegerField(default=1,verbose_name="Orden de aparición",help_text="Número que define el orden de aparición (de menor a mayor)")
    script = models.TextField(verbose_name="Código del Banner",help_text="Copia y pega el código HTML del banner generado")
    activo = models.BooleanField(default=True,verbose_name="Activo",help_text="Indica si el banner se muestra en la página")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")
    
    class Meta:
        ordering = ['position', 'orden']
        verbose_name = "Banner Publicitario"
        verbose_name_plural = "Banners Publicitarios"
    
    def _str_(self):
        return f"{self.get_position_display()} - Orden {self.orden}"

# Vista Programa
class Programa(models.Model):
    titulo = models.CharField(max_length=200)
    host = models.CharField(max_length=200,blank=True,null=True)
    duracion = models.CharField(max_length=10,blank=True,null=True,help_text="Ejemplo: 4:47")
    url_reproducir = models.URLField(blank=True,null=True,help_text="URL externa de reproducción (opcional)")
    audio = models.FileField(upload_to='programas/audios/',blank=True,null=True,validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg', 'm4a'])],help_text="Sube un archivo de audio (.mp3, .wav, .ogg, .m4a)")
    fecha_creacion = models.DateField(auto_now_add=True)

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

    def _str_(self):
        return f'{self.dia_semana} - {self.programa}'
    


# Anunciate con nosotros

class PublicidadContacto(models.Model):
    nombre = models.CharField(max_length=150)
    cargo = models.CharField(max_length=150)
    empresa = models.CharField(max_length=200)
    telefono = models.CharField(max_length=50)
    email = models.EmailField()
    comentarios = models.TextField(blank=True, null=True)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.empresa}"
    


class ContactMessage(models.Model):
    """
    Modelo para almacenar los mensajes enviados desde el formulario de contacto.
    """
    nombre = models.CharField("Nombre", max_length=100)
    telefono = models.CharField("Teléfono", max_length=20)
    email = models.EmailField("Correo electrónico")
    mensaje = models.TextField("Mensaje", blank=True)
    date_created = models.DateTimeField("Fecha de envío", auto_now_add=True)

    class Meta:
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.nombre} - {self.email} ({self.date_created:%Y-%m-%d %H:%M})"

