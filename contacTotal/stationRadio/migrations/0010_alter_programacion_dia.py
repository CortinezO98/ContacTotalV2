# Generated by Django 5.1.5 on 2025-03-29 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stationRadio', '0009_alter_programacion_dia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programacion',
            name='dia',
            field=models.DateField(),
        ),
    ]
