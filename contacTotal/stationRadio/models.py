from django.db import models
from pytz import timezone
import pytz
from datetime import datetime
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
import os


# Podcast
class PodcastSection(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='podcasts_covers/', blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True, editable=False)
    featured = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Sección de Podcast'
        verbose_name_plural = 'Secciones de Podcast'
        ordering = ['-date_created']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(PodcastSection, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class PodcastAudio(models.Model):
    podcast_section = models.ForeignKey(PodcastSection, related_name='audios', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    audio_file = models.FileField(upload_to='podcasts_audio/')
    audio_link = models.URLField(blank=True, null=True, help_text="Enlace embed de YouTube, por ejemplo")
    duration = models.CharField(max_length=20, blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Audio de Podcast'
        verbose_name_plural = 'Audios de Podcast'
        ordering = ['-date_created']

    def __str__(self):
        return self.title

class PodcastVideo(models.Model):
    podcast_section = models.ForeignKey(PodcastSection, related_name='videos', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_link = models.URLField(blank=True, null=True, help_text="Enlace embed de YouTube, por ejemplo")
    cover_image = models.ImageField(upload_to='podcasts_video_covers/', blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Video de Podcast'
        verbose_name_plural = 'Videos de Podcast'
        ordering = ['-date_created']

    def __str__(self):
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



class SeccionChoices(models.TextChoices):
    ACTUALIDAD_LOCAL           = 'actualidad_local',        'Actualidad local'
    ACTUALIDAD_NACIONAL        = 'actualidad_nacional',     'Actualidad nacional'
    ANIVERSARIO                = 'aniversario',             'Aniversario'
    BUENA_VIDA                 = 'buena_vida',              'Buena vida'
    CALENDARIO_DE_EVENTOS      = 'calendario_de_eventos',   'Calendario de eventos'
    CAMINO_AL_EXITO            = 'camino_al_exito',         'Camino al éxito'
    COMUNIDAD                  = 'comunidad',               'Comunidad'
    CASOS_DE_FAMILIA           = 'casos_de_familia',        'Casos de familia'
    CUIDE_SU_SALUD             = 'cuide_su_salud',          'Cuide su salud'
    DE_COMPRAS                 = 'de_compras',              'De compras'
    DE_NUESTROS_CONSULADOS     = 'de_nuestros_consulados',  'De nuestros consulados'
    DE_SU_BOLSILLO             = 'de_su_bolsillo',          'De su bolsillo'
    DE_SU_RONCO_PECHO          = 'de_su_ronco_pecho',       'De su ronco pecho'
    DESTACADO                  = 'destacado',               'Destacado'
    DESTINOS                   = 'destinos',                'Destinos'
    DETRAS_DE_CAMARAS          = 'detras_de_camaras',       'Detrás de cámaras'
    DIA_DEL_PADRE              = 'dia_del_padre',           'Día del padre'
    DIA_DE_LA_MADRE            = 'dia_de_la_madre',         'Día de la madre'
    ECHANDOLE_GANAS            = 'echandole_ganas',         'Echándole ganas'
    EDITORIAL                  = 'editorial',               'Editorial'
    ELECCIONES                 = 'elecciones',              'Elecciones'
    EN_LA_JUGADA               = 'en_la_jugada',            'En la jugada'
    EN_LA_MIRA                 = 'en_la_mira',              'En la mira'
    EN_PANTALLA                = 'en_pantalla',             'En pantalla'
    ENTERATE                   = 'enterate',                'Entérate'
    ESPECIAL                   = 'especial',                'Especial'
    EXCLUSIVO                  = 'exclusivo',               'Exclusivo'
    ESTILO_Y_BELLEZA           = 'estilo_y_belleza',        'Estilo y belleza'
    ESTRENOS                   = 'estrenos',                'Estrenos'
    FAMOSOS_DE_AQUI_Y_ALLA     = 'famosos_de_aqui_y_alla',  'Famosos de aquí y allá'
    GENTE_EN_CONTACTO_TOTAL    = 'gente_en_contacto_total', 'Gente en Contacto total'
    INMIGRACION_AL_DIA         = 'inmigracion_al_dia',      'Inmigración al día'
    HERENCIA_HISPANA           = 'herencia_hispana',        'Herencia Hispana'
    MUNDO_EMPRESARIAL          = 'mundo_empresarial',       'Mundo empresarial'
    MUY_PERSONAL               = 'muy_personal',            'Muy personal'
    NUESTRA_MUSICA             = 'nuestra_musica',          'Nuestra música'
    ORGULLO_HISPANO            = 'orgullo_hispano',         'Orgullo hispano'
    PANORAMA_LOCAL             = 'panorama_local',          'Panorama local'
    PANORAMA_MUNDIAL           = 'panorama_mundial',        'Panorama mundial'
    PANORAMA_NACIONAL          = 'panorama_nacional',       'Panorama nacional'
    PANTALLA_CHICA             = 'pantalla_chica',          'Pantalla chica'
    PANTALLA_GRANDE            = 'pantalla_grande',         'Pantalla grande'
    PARA_CHUPARSE_LOS_DEDOS    = 'para_chuparse_los_dedos', 'Para chuparse los dedos'
    PRIMER_PLANO               = 'primer_plano',            'Primer plano'
    PUNTO_DE_VISTA             = 'punto_de_vista',          'Punto de vista'
    QUE_NO_LE_PASE_A_USTED     = 'que_no_le_pase_a_usted',  'Que no le pase a usted'
    SALUD_Y_BELLEZA            = 'salud_y_belleza',         'Salud y belleza'
    SI_SE_PUEDE                = 'si_se_puede',             'Sí se puede'
    STREAMING                  = 'streaming',               'Streaming'
    TALENTO_LOCAL              = 'talento_local',           'Talento local'
    VIDA_DE_MASCOTA            = 'vida_de_mascota',         'Vida de mascota'
    VIDA_DE_PAREJA             = 'vida_de_pareja',          'Vida de pareja'
    VIDA_SEGURA                = 'vida_segura',             'Vida segura'
    VOCES                      = 'voces',                   'Voces'
    YO_RECOMIENDO              = 'yo_recomiendo',           'Yo recomiendo'
    ZONA_DIGITAL               = 'zona_digital',            'Zona digital'


class Articulo(TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
    ]

    edicion = models.ForeignKey(EdicionRevista, related_name='articulos', on_delete=models.CASCADE)
    seccion = models.CharField('Sección', max_length=50, choices=SeccionChoices.choices, default=SeccionChoices.ACTUALIDAD_LOCAL)
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, editable=False)
    portada = models.ImageField(upload_to='revistas/articulos/')
    portada_pie_de_foto = models.CharField(max_length=255,blank=True,help_text="Pie de foto de la portada")
    portada_credito = models.CharField(max_length=255,blank=True,help_text="Crédito de la imagen de portada")
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

class ImagenArticulo(models.Model):
    articulo = models.ForeignKey('Articulo', on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='revistas/articulos/imagenes/')
    contenido = models.TextField(blank=True,help_text="Texto o descripción que acompañará a esta imagen")
    pie_de_foto = models.CharField(max_length=255, blank=True, help_text="Texto descriptivo o pie de foto")
    credito = models.CharField(max_length=255, blank=True, help_text="Nombre del autor o fuente")

    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición en el contenido")

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"Imagen para {self.articulo.titulo}"


    

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
    
#Modelo para el horario de Twitch

class TwitchSchedule(models.Model):
    DAY_CHOICES = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    day_of_week = models.IntegerField(
        choices=DAY_CHOICES,
        verbose_name="Día de la semana"
    )
    start_time = models.TimeField(
        verbose_name="Hora de inicio"
    )
    end_time = models.TimeField(
        verbose_name="Hora de fin"
    )
    twitch_channel = models.CharField(
        max_length=100, 
        default='contactototal',
        verbose_name="Canal de Twitch"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    
    class Meta:
        verbose_name = "Horario de Twitch"
        verbose_name_plural = "Horarios de Twitch"
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.get_day_of_week_display()} de {self.start_time.strftime('%H:%M')} a {self.end_time.strftime('%H:%M')}"


# Carrusel de Noticias (Index)
class CarouselNews(models.Model):
    title = models.CharField(max_length=255)
    publication_date = models.DateField()
    author = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='carousel_news/')
    pie_de_foto       = models.CharField("Pie de foto",max_length=255,blank=True,help_text="Texto descriptivo o pie de foto de la imagen")
    credit = models.CharField("Crédito de la imagen",max_length=255,blank=True,help_text="Autor o fuente de la imagen")
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
    pie_de_foto = models.CharField("Pie de foto",max_length=255,blank=True,help_text="Texto descriptivo o pie de foto ")
    credit = models.CharField("Crédito de la imagen",max_length=255,blank=True,help_text="Autor o fuente de la imagen")
    author = models.CharField(max_length=255)
    publication_date = models.DateField()
    short_description = models.TextField(help_text="Descripción corta de la noticia")
    slug = models.SlugField(unique=True, blank=True, editable=False)

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
    link = models.URLField(blank=True, null=True,help_text="A dónde redirige el anuncio al hacer clic sobre la imagen")
    
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
    titulo = models.CharField(max_length=200, blank=True, null=True)
    host = models.CharField(max_length=200, blank=True, null=True)
    duracion = models.CharField(max_length=10, blank=True, null=True, help_text="Ejemplo: 4:47")
    nombre_archivo = models.CharField(max_length=255, blank=True, null=True)
    peso_archivo = models.CharField(max_length=20, blank=True, null=True, help_text="Tamaño del audio (ej: 3.5 MB)")
    url_reproducir = models.URLField(blank=True, null=True, help_text="URL externa de reproducción (opcional)")
    audio = models.FileField(
        upload_to='programas/audios/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg', 'm4a'])],
        help_text="Sube un archivo de audio (.mp3, .wav, .ogg, .m4a)"
    )
    fecha_creacion = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.audio:
            try:
                audio_path = self.audio.path
                audio_file = MutagenFile(audio_path, easy=True)
                full_file = MutagenFile(audio_path)

                # Duración
                if full_file and full_file.info.length:
                    total_seconds = int(full_file.info.length)
                    minutes = total_seconds // 60
                    seconds = total_seconds % 60
                    self.duracion = f"{minutes}:{seconds:02d}"

                # Título desde metadata
                if not self.titulo:
                    if isinstance(audio_file, EasyID3):
                        self.titulo = audio_file.get("title", [None])[0]
                    elif isinstance(audio_file, MP4):
                        self.titulo = audio_file.tags.get('\xa9nam', [None])[0]

                # Nombre y tamaño del archivo
                self.nombre_archivo = os.path.basename(audio_path)
                file_size = os.path.getsize(audio_path) / (1024 * 1024)  # MB
                self.peso_archivo = f"{file_size:.2f} MB"

                # Fecha de creación desde metadata (si aplica)
                if isinstance(full_file, MP4):
                    creation_time = full_file.tags.get('©day', [None])[0]
                    if creation_time:
                        try:
                            self.fecha_creacion = datetime.strptime(creation_time, "%Y-%m-%d").date()
                        except:
                            pass
            except Exception as e:
                print(f"Error extrayendo metadatos del audio: {e}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo or "Programa sin título"




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

