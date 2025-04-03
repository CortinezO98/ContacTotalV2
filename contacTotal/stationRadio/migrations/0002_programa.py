# Generated by Django 5.1.5 on 2025-03-29 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stationRadio', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Programa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('host', models.CharField(max_length=200)),
                ('duracion', models.DecimalField(decimal_places=2, max_digits=5)),
                ('url_reproducir', models.URLField()),
            ],
        ),
    ]
