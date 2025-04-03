from django.contrib import admin
from .models import *

@admin.register(EdicionRevista)
class EdicionRevistaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_publicacion', 'url')  
    search_fields = ('titulo', 'descripcion')  
    list_filter = ('fecha_publicacion',)
    



@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'host', 'duracion', 'url_reproducir')  
    search_fields = ('titulo', 'host')  
    list_filter = ('host',)  


@admin.register(Programacion)
class ProgramacionAdmin(admin.ModelAdmin):
    list_display = ('dia', 'programa', 'hora', 'zona_horaria_usuario', 'hora_mexico', 'hora_argentina', 'hora_eeuu', 'hora_bogota')

    def hora_mexico(self, obj):
        return obj.get_otra_zona_horaria('America/Mexico_City')
    hora_mexico.short_description = 'Hora México'

    def hora_argentina(self, obj):
        return obj.get_otra_zona_horaria('America/Argentina/Buenos_Aires')
    hora_argentina.short_description = 'Hora Argentina'

    def hora_bogota(self, obj):
        return obj.get_otra_zona_horaria('America/Bogota')
    hora_bogota.short_description = 'Hora Bogotá'

    def hora_eeuu(self, obj):
        return obj.get_otra_zona_horaria('America/New_York')
    hora_eeuu.short_description = 'Hora EEUU'