from django.db import models
from pytz import timezone
import pytz
from datetime import datetime
from .models import *
class Podcast(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    audio_file = models.FileField(upload_to='podcasts/')
    cover_image = models.ImageField(upload_to='podcasts_covers/')
    date_created = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title




class EdicionRevista(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='revistas/')
    fecha_publicacion = models.DateField()
    url = models.URLField()

    def __str__(self):
        return self.titulo



class Programa(models.Model):
    titulo = models.CharField(max_length=200)
    host = models.CharField(max_length=200)
    duracion = models.DecimalField(max_digits=5, decimal_places=2)  
    url_reproducir = models.URLField()  

    def __str__(self):
        return self.titulo



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