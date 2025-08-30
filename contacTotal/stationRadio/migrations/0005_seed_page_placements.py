# stationRadio/migrations/0005_seed_page_placements.py
from django.db import migrations

def seed(apps, schema_editor):
    PagePlacement = apps.get_model('stationRadio', 'PagePlacement')

    slugs = [
        'revista', 'revista_detail', 'programas', 'podcast', 'podcast_detail',
        'quienesSomos', 'programacion', 'contacto', 'noticia_detalle',
        'anunciate', 'articulo_detail'
    ]

    # Nombres bonitos por slug (opcional)
    display_names = {
        'revista': 'Revista',
        'revista_detail': 'Revista (detalle)',
        'programas': 'Programas',
        'podcast': 'Podcast',
        'podcast_detail': 'Podcast (detalle)',
        'quienesSomos': 'Quiénes Somos',
        'programacion': 'Programación',
        'contacto': 'Contacto',
        'noticia_detalle': 'Noticia (detalle)',
        'anunciate': 'Anúnciate',
        'articulo_detail': 'Artículo (detalle)',
    }

    for s in slugs:
        PagePlacement.objects.get_or_create(
            slug=s,
            defaults={'name': display_names.get(s, s)}
        )

def unseed(apps, schema_editor):
    # No borramos nada por seguridad; si lo quisieras, podrías filtrar por esos slugs y eliminarlos.
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('stationRadio', '0004_pageplacement_alter_announcement_options_and_more'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
