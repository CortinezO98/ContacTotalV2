# Generated by Django 5.1.5 on 2025-03-29 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stationRadio', '0007_alter_programacion_zona_horaria_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programacion',
            name='hora',
            field=models.TimeField(),
        ),
    ]
