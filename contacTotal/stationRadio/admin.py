from django.contrib import admin
from import_export.admin import ExportMixin
from django.utils.html import format_html
from import_export import resources
from django.utils.translation import gettext_lazy as _
import os
import mutagen
from django import forms
from .models import *
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin



admin.site.site_header = "Administración Revista Contacto Total"
admin.site.site_title = "Panel de Contacto Total"
admin.site.index_title = "Bienvenido al Panel de Administración"

@admin.register(TwitchSchedule)
class TwitchScheduleAdmin(admin.ModelAdmin):
    list_display = ('get_day_display', 'start_time', 'end_time', 'twitch_channel', 'is_active')
    list_filter = ('day_of_week', 'is_active')
    search_fields = ('twitch_channel',)
    list_editable = ('is_active',)
    
    def get_day_display(self, obj):
        return obj.get_day_of_week_display()
    get_day_display.short_description = 'Día de la semana'
    get_day_display.admin_order_field = 'day_of_week'


class PodcastAudioInline(admin.TabularInline):
    model = PodcastAudio
    extra = 1

class PodcastVideoInline(admin.TabularInline):
    model = PodcastVideo
    extra = 1

@admin.register(PodcastSection)
class PodcastSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'featured', 'date_created', 'cover_image_preview')
    readonly_fields = ('slug', 'date_created', 'cover_image_preview')
    search_fields = ('title',)
    list_per_page = 25
    inlines = [PodcastAudioInline, PodcastVideoInline]

    fieldsets = (
        ('Información general', {
            'fields': ('title', 'description', 'cover_image', 'cover_image_preview', 'featured')
        }),
        ('Información automática', {
            'fields': ('slug', 'date_created'),
            'classes': ('collapse',)
        }),
    )

    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="120" style="border-radius:6px;">', obj.cover_image.url)
        return "—"
    cover_image_preview.short_description = "Vista previa de portada"



@admin.register(PodcastAudio)
class PodcastAudioAdmin(admin.ModelAdmin):
    list_display = ('title', 'podcast_section', 'duration', 'date_created')
    list_filter = ('podcast_section',)
    search_fields = ('title',)
    autocomplete_fields = ['podcast_section']
    list_per_page = 25




@admin.register(PodcastVideo)
class PodcastVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'podcast_section', 'date_created', 'cover_image_preview')
    list_filter = ('podcast_section',)
    search_fields = ('title',)
    autocomplete_fields = ['podcast_section']
    list_per_page = 25

    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="120" style="border-radius:6px;">', obj.cover_image.url)
        return "—"
    cover_image_preview.short_description = "Vista previa de portada"




@admin.action(description="📢 Marcar como Publicado")
def make_published(modeladmin, request, queryset):
    for obj in queryset:
        if obj.status != 'published':
            obj.status = 'published'
            obj.save() 



@admin.action(description="🚫 Marcar como Borrador")
def make_draft(modeladmin, request, queryset):
    queryset.update(status='draft')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display    = ('name', 'slug')
    readonly_fields = ('slug',)


class ArticuloInline(admin.TabularInline):
    model            = Articulo
    extra            = 1
    fields           = (
        'titulo', 'portada', 'descripcion_corta', 'contenido',
        'autor', 'external_url', 'es_principal', 'orden', 'status'
    )
    readonly_fields  = ('slug', 'fecha_publicado', 'view_count')
    sortable_by      = ('orden',)
    show_change_link = True


@admin.register(EdicionRevista)
class EdicionRevistaAdmin(admin.ModelAdmin):
    list_display    = (
        'titulo', 'fecha_publicacion', 'status',
        'num_articulos', 'is_pdf_only', 'link_preview', 'imagen_preview'
    )
    list_filter     = ('status', 'fecha_publicacion')
    date_hierarchy  = 'fecha_publicacion'
    search_fields   = ('titulo', 'descripcion')
    readonly_fields = ('slug', 'created_at', 'updated_at', 'fecha_publicacion', 'imagen_preview')
    inlines         = [ArticuloInline]
    actions         = [make_published, make_draft]

    fieldsets = (
        (None, {
            'fields': ('titulo', 'descripcion', 'imagen', 'imagen_preview', 'pdf', 'status')
        }),
        ('Metadatos', {
            'fields': ('fecha_publicacion', 'slug', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def num_articulos(self, obj):
        return obj.articulos.count()
    num_articulos.short_description = "Artículos"

    def is_pdf_only(self, obj):
        return obj.is_pdf_only()
    is_pdf_only.boolean = True
    is_pdf_only.short_description = "Solo PDF?"

    def link_preview(self, obj):
        url = obj.get_absolute_url()
        return format_html('<a href="{}" target="_blank">Abrir</a>', url)
    link_preview.short_description = "Enlace"

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="100" style="border-radius: 4px;" />', obj.imagen.url)
        return "Sin imagen"
    imagen_preview.short_description = "Vista previa"

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            base_slug = slugify(obj.titulo)
            slug = base_slug
            num = 1
            while EdicionRevista.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            obj.slug = slug
        super().save_model(request, obj, form, change)



class ImagenArticuloInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ImagenArticulo
    fields = ('imagen','contenido', 'imagen_preview', 'pie_de_foto', 'credito', 'orden')
    readonly_fields = ('imagen_preview',)
    extra = 1
    ordering = ['orden']

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" width="100" style="border-radius:4px;"/>',
                obj.imagen.url
            )
        return "Sin imagen"
    imagen_preview.short_description = "Vista previa"

@admin.register(Articulo)
class ArticuloAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display      = ('titulo', 'edicion', 'seccion_display', 'es_principal','status', 'orden', 'view_count', 'external_url', 'portada_preview')
    list_filter       = ('status', 'es_principal', 'edicion', 'seccion')
    date_hierarchy    = 'fecha_publicado'
    search_fields     = ('titulo', 'descripcion_corta', 'contenido', 'autor')
    readonly_fields   = ('slug', 'fecha_publicado', 'created_at', 'updated_at', 'view_count', 'portada_preview')
    list_editable     = ('es_principal', 'orden', 'status')
    actions           = [make_published, make_draft]
    filter_horizontal = ('tags',)
    inlines = [ImagenArticuloInline]

    fieldsets = (
        (None, {
            'fields': ('edicion', 'seccion', 'titulo', 'portada', 'portada_preview','portada_pie_de_foto', 'portada_credito','descripcion_corta', 'contenido', 'autor','external_url', 'tags')
        }),
        ('Opciones', {
            'fields': ('es_principal', 'orden', 'status')
        }),
        ('Metadatos', {
            'fields': ('fecha_publicado', 'slug', 'view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Sección', ordering='seccion')
    def seccion_display(self, obj):
        return obj.get_seccion_display()

    def portada_preview(self, obj):
        if obj.portada:
            return format_html(
                '<img src="{}" width="100" style="border-radius:4px;"/>',
                obj.portada.url
            )
        return "Sin imagen"
    portada_preview.short_description = "Vista previa"

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            base_slug = slugify(obj.titulo)
            slug = base_slug
            num = 1
            while Articulo.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            obj.slug = slug
        super().save_model(request, obj, form, change)





@admin.register(MainVideo)
class MainVideoAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    list_per_page = 25

@admin.register(CarouselNews)
class CarouselNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'publication_date', 'author')
    search_fields = ('title', 'description', 'author')
    list_filter = ('publication_date',)
    list_per_page = 25

@admin.register(MainNews)
class MainNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'publication_date', 'author')
    search_fields = ('title', 'short_description', 'author')
    list_filter = ('publication_date',)
    list_per_page = 25

@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'link', 'imagen_preview', 'enlace_destino')
    search_fields = ('titulo', 'link')
    list_per_page = 25
    readonly_fields = ('imagen_preview',)

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" width="100" style="border-radius:4px;" />',
                obj.imagen.url
            )
        return "—"
    imagen_preview.short_description = "Vista previa"

    def enlace_destino(self, obj):
        if obj.link:
            return format_html(
                '<a href="{}" target="_blank">Abrir enlace</a>',
                obj.link
            )
        return "—"
    enlace_destino.short_description = "Enlace"

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'position', 'active',
        'has_script', 'has_images',
        'date_created', 'image_preview_desktop'
    )
    # ⬇️ Añadimos show_in_all y placements al filtro
    list_filter  = ('active', 'position', 'date_created', 'show_in_all', 'placements')
    search_fields = ('title',)
    actions = ['activar_anuncios', 'desactivar_anuncios']
    list_per_page = 25

    # ⬇️ Para elegir varias vistas cómodamente
    filter_horizontal = ('placements',)

    readonly_fields = (
        'image_preview', 'image_preview_desktop', 'image_preview_tablet', 'image_preview_mobile',
        'script_preview', 'date_created',
    )

    fieldsets = (
        ('Información', {
            'fields': ('title', 'position', 'active', 'starts_at', 'ends_at')
        }),
        ('Destino', {
            'fields': ('link',)
        }),
        # ⬇️ NUEVO bloque de visibilidad por vista
        ('Visibilidad', {
            'fields': ('show_in_all', 'placements')
        }),
        ('Creatividad (prioridad: script > imágenes)', {
            'fields': (
                'custom_script', 'script_preview',
                'image', 'image_desktop', 'image_tablet', 'image_mobile',
                'image_preview', 'image_preview_desktop', 'image_preview_tablet', 'image_preview_mobile'
            )
        }),
        ('Metadatos', {
            'fields': ('date_created',),
            'classes': ('collapse',)
        }),
    )

    # --- Helpers visuales (igual que ya tenías) ---
    def has_script(self, obj):
        return bool(obj.custom_script)
    has_script.boolean = True
    has_script.short_description = "Script"

    def has_images(self, obj):
        return any([
            obj.image,
            getattr(obj, 'image_desktop', None),
            getattr(obj, 'image_tablet', None),
            getattr(obj, 'image_mobile', None)
        ])
    has_images.boolean = True
    has_images.short_description = "Imágenes"

    def script_preview(self, obj):
        if obj.custom_script:
            content = (obj.custom_script[:160] + '...') if len(obj.custom_script) > 160 else obj.custom_script
            return format_html('<code style="white-space:pre-wrap; font-size:11px;">{}</code>', content)
        return "—"
    script_preview.short_description = "Vista previa script"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="120" style="border-radius:6px;">', obj.image.url)
        return "—"
    image_preview.short_description = "Fallback"

    def image_preview_desktop(self, obj):
        if getattr(obj, 'image_desktop', None):
            return format_html('<img src="{}" width="120" style="border-radius:6px;">', obj.image_desktop.url)
        return "—"
    image_preview_desktop.short_description = "Desktop"

    def image_preview_tablet(self, obj):
        if getattr(obj, 'image_tablet', None):
            return format_html('<img src="{}" width="120" style="border-radius:6px;">', obj.image_tablet.url)
        return "—"
    image_preview_tablet.short_description = "Tablet"

    def image_preview_mobile(self, obj):
        if getattr(obj, 'image_mobile', None):
            return format_html('<img src="{}" width="120" style="border-radius:6px;">', obj.image_mobile.url)
        return "—"
    image_preview_mobile.short_description = "Mobile"

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
    list_display = ('id', 'position', 'orden', 'activo', 'has_script', 'has_any_image', 'preview_desktop', 'actualizado_en')
    list_filter  = ('position', 'activo')
    search_fields = ('script', 'link')
    ordering = ('position', 'orden')
    list_per_page = 25
    readonly_fields = ('preview_desktop','preview_tablet','preview_mobile','creado_en','actualizado_en')

    fieldsets = (
        ('Ubicación y estado', {'fields': ('position','orden','activo')}),
        ('Enlace', {'fields': ('link',)}),
        ('Creatividad (prioridad: script > imágenes)', {
            'fields': (
                'script',
                'image_desktop', 'image_tablet', 'image_mobile',
                'preview_desktop', 'preview_tablet', 'preview_mobile'
            )
        }),
        ('Fechas', {'fields': ('creado_en','actualizado_en'), 'classes': ('collapse',)})
    )

    def has_script(self, obj):
        return bool(obj.script)
    has_script.boolean = True
    has_script.short_description = "Script"

    def has_any_image(self, obj):
        return any([obj.image_desktop, obj.image_tablet, obj.image_mobile])
    has_any_image.boolean = True
    has_any_image.short_description = "Imágenes"

    def preview_desktop(self, obj):
        return format_html('<img src="{}" width="120" style="border-radius:6px;">', obj.image_desktop.url) if obj.image_desktop else "—"
    preview_desktop.short_description = "Desktop"

    def preview_tablet(self, obj):
        return format_html('<img src="{}" width="120" style="border-radius:6px;">', obj.image_tablet.url) if obj.image_tablet else "—"
    preview_tablet.short_description = "Tablet"

    def preview_mobile(self, obj):
        return format_html('<img src="{}" width="120" style="border-radius:6px;">', obj.image_mobile.url) if obj.image_mobile else "—"
    preview_mobile.short_description = "Mobile"

@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'host', 'duracion', 'nombre_archivo', 'peso_archivo', 'fecha_creacion', 'reproductor_audio'
    )
    readonly_fields = (
        'duracion', 'nombre_archivo', 'peso_archivo', 'fecha_creacion', 'reproductor_audio'
    )
    search_fields = ('titulo', 'host')
    list_filter = ('host', 'fecha_creacion')
    list_per_page = 25

    fieldsets = (
        ('Información del programa', {
            'fields': (
                'titulo', 'host', 'audio', 'url_reproducir',
            ),
        }),
        ('Metadatos automáticos', {
            'fields': ('duracion', 'nombre_archivo', 'peso_archivo', 'fecha_creacion', 'reproductor_audio'),
            'classes': ('collapse',),
        }),
    )

    def reproductor_audio(self, obj):
        if obj.audio:
            return format_html(
                '<audio controls style="width: 100%;">'
                '<source src="{}" type="audio/mpeg">'
                'Tu navegador no soporta el elemento de audio.'
                '</audio>',
                obj.audio.url
            )
        return "No hay audio"

    reproductor_audio.short_description = "Reproductor"


class ProgramacionAdminForm(forms.ModelForm):
    DAYS_CHOICES = [
        ('mon', 'Lunes'),
        ('tue', 'Martes'),
        ('wed', 'Miércoles'),
        ('thu', 'Jueves'),  
        ('fri', 'Viernes'),
        ('sat', 'Sábado'),
        ('sun', 'Domingo'),
    ]
    
    dias_semana = forms.MultipleChoiceField(
        choices=DAYS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Días de la semana'
    )
    
    class Meta:
        model = Programacion
        fields = '__all__'

@admin.register(Programacion)
class ProgramacionAdmin(admin.ModelAdmin):
    form = ProgramacionAdminForm  # Agregar esta línea
    
    list_display = (
        'programa',
        'get_dias',
        'hora_inicio',
        'hora_fin',
        'zona_horaria_usuario',
        'hora_mexico',
        'hora_argentina',
        'hora_bogota',
        'hora_eeuu',
    )
    list_per_page = 25

    def get_dias(self, obj):
        return obj.dias_as_texto()
    get_dias.short_description = 'Días'

    def hora_mexico(self, obj):
        return obj.get_otra_zona_horaria('America/Mexico_City', obj.hora_inicio)
    hora_mexico.short_description = 'Inicio (México)'

    def hora_argentina(self, obj):
        return obj.get_otra_zona_horaria('America/Argentina/Buenos_Aires', obj.hora_inicio)
    hora_argentina.short_description = 'Inicio (Argentina)'

    def hora_bogota(self, obj):
        return obj.get_otra_zona_horaria('America/Bogota', obj.hora_inicio)
    hora_bogota.short_description = 'Inicio (Bogotá)'

    def hora_eeuu(self, obj):
        return obj.get_otra_zona_horaria('America/New_York', obj.hora_inicio)
    hora_eeuu.short_description = 'Inicio (EE.UU.)'

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
    list_per_page = 25

class ContactMessageResource(resources.ModelResource):
    class Meta:
        model = ContactMessage
        fields = ('id', 'nombre', 'telefono', 'email', 'mensaje', 'date_created')

@admin.register(ContactMessage)
class ContactMessageAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ContactMessageResource
    list_display = ('nombre', 'email', 'telefono', 'short_message', 'date_created')
    search_fields = ('nombre', 'email', 'telefono')
    list_filter = ('date_created',)
    readonly_fields = ('nombre', 'email', 'telefono', 'mensaje', 'date_created')
    list_per_page = 25

    def short_message(self, obj):
        return obj.mensaje[:50] + ('...' if len(obj.mensaje) > 50 else '')
    short_message.short_description = 'Mensaje'
