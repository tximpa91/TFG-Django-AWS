# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-07-11 10:44
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alimento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('tipo', models.CharField(choices=[('LA', 'Lacteos'), ('HU', 'Huevos'), ('CA', 'Carnicos'), ('MA', 'Pescados, moluscos, reptiles, crustaceos'), ('AC', 'Grasas y Aceites'), ('CE', 'Cereales'), ('LE', 'Legumbres, semillas y frutos secos'), ('VE', 'Verduras y Hortalizas'), ('FR', 'Frutas'), ('AZ', 'Azucar y Chocolates'), ('BE', 'Bebidas'), ('MI', 'Misc\xe1lenea'), ('PR', 'Producto de uso nutricional')], max_length=2)),
                ('calorias', models.IntegerField()),
                ('grasa', models.FloatField()),
                ('proteina', models.FloatField()),
                ('agua', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_cita', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genero', models.CharField(choices=[('M', 'Masculino'), ('F', 'Femenino')], max_length=1)),
                ('estatura', models.FloatField()),
                ('peso', models.FloatField()),
                ('diabetico', models.BooleanField()),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comida',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_comida', models.DateField(default=datetime.datetime.now)),
                ('porcion', models.IntegerField(default=1)),
                ('glucosa', models.IntegerField(blank=True, null=True)),
                ('tipo', models.CharField(choices=[('DE', 'Desayuno'), ('CO', 'Comida'), ('ME', 'Merienda'), ('CE', 'Cena')], max_length=2)),
                ('alimentos', models.ManyToManyField(to='alimentus.Alimento')),
                ('paciente', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='alimentus.Cliente')),
            ],
        ),
        migrations.CreateModel(
            name='Historico',
            fields=[
                ('FechaHistorica', models.DateTimeField(primary_key=True, serialize=False)),
                ('username', models.CharField(blank=True, max_length=60, null=True)),
                ('estatura', models.FloatField()),
                ('peso', models.FloatField()),
                ('diabetico', models.BooleanField()),
            ],
        ),
        migrations.AddField(
            model_name='cita',
            name='paciente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alimentus.Cliente'),
        ),
    ]