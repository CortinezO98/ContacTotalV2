# Generated by Django 5.1.5 on 2025-04-04 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stationRadio', '0012_anuncio_carouselnews_mainnews'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edicionrevista',
            name='fecha_publicacion',
            field=models.DateField(auto_now_add=True),
        ),
    ]
