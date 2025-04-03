# Generated by Django 5.1.5 on 2025-03-29 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stationRadio', '0003_programacion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='programacion',
            name='zona_horaria',
        ),
        migrations.AddField(
            model_name='programacion',
            name='zona_horaria_usuario',
            field=models.CharField(choices=[('America/Mexico_City', 'Mexico'), ('America/Bogota', 'Bogota'), ('America/Argentina/Buenos_Aires', 'Argentina'), ('Chile', 'Chile'), ('America/New_York', 'EEUU')], default='America/Bogota', max_length=50),
            preserve_default=False,
        ),
    ]
