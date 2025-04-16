from django.contrib import admin
from import_export.admin import ExportMixin
from django.utils.html import format_html
from import_export import resources
from .models import *

class PodcastAudioInline(admin.TabularInline):
    model = PodcastAudio
    extra = 1

class PodcastVideoInline(admin.TabularInline):
    model = PodcastVideo
    extra = 1



@admin.register(EdicionRevista)
class EdicionRevistaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_publicacion', 'url')  
    search_fields = ('titulo', 'descripcion')  
    list_filter = ('fecha_publicacion',)
    


@admin.register(PodcastSection)
class PodcastSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_created')
    readonly_fields = ('slug',)
    inlines = [PodcastAudioInline, PodcastVideoInline]

@admin.register(PodcastAudio)
class PodcastAudioAdmin(admin.ModelAdmin):
    list_display = ('title', 'podcast_section', 'date_created')
    list_filter = ('podcast_section',)
    search_fields = ('title',)

@admin.register(PodcastVideo)
class PodcastVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'podcast_section', 'date_created')
    list_filter = ('podcast_section',)
    search_fields = ('title',)


@admin.register(MainVideo)
class MainVideoAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(CarouselNews)
class CarouselNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'publication_date', 'author')
    search_fields = ('title', 'description', 'author')
    list_filter = ('publication_date',)

@admin.register(MainNews)
class MainNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'publication_date', 'author')
    search_fields = ('title', 'short_description', 'author')
    list_filter = ('publication_date',)


@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    list_display = ('titulo',)
    search_fields = ('titulo',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'position', 'active', 'image_preview', 'script_preview', 'date_created')
    list_filter = ('active', 'position', 'date_created')
    search_fields = ('title',)
    readonly_fields = ('image_preview', 'script_preview')
    actions = ['activar_anuncios', 'desactivar_anuncios']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" style="border-radius:6px;" />', obj.image.url)
        return "—"
    image_preview.short_description = "Vista previa imagen"

    def script_preview(self, obj):
        if obj.custom_script:
            content = (obj.custom_script[:100] + '...') if len(obj.custom_script) > 100 else obj.custom_script
            return format_html('<code style="white-space:pre-wrap; font-size:11px;">{}</code>', content)
        return "—"
    script_preview.short_description = "Vista previa script"

    @admin.action(description="✅ Activar anuncios seleccionados")
    def activar_anuncios(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(request, f"{updated} anuncio(s) activado(s) correctamente.")

    @admin.action(description="🚫 Desactivar anuncios seleccionados")
    def desactivar_anuncios(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(request, f"{updated} anuncio(s) desactivado(s) correctamente.")



@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'position', 'orden', 'activo', 'actualizado_en')
    list_filter = ('position', 'activo')
    search_fields = ('script',)
    ordering = ('position', 'orden')


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



# Datos de Anunciate con nosotros

class PublicidadContactoResource(resources.ModelResource):
    class Meta:
        model = PublicidadContacto
        fields = ('id', 'nombre', 'cargo', 'empresa', 'telefono', 'email', 'comentarios', 'fecha_envio')

@admin.register(PublicidadContacto)
class PublicidadContactoAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = PublicidadContactoResource
    list_display = ('nombre', 'empresa', 'email', 'telefono', 'fecha_envio')
    search_fields = ('nombre', 'empresa', 'email')
    list_filter = ('fecha_envio',)

