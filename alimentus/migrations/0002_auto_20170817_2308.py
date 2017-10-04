# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-08-17 21:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alimentus', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comida',
            name='porcion',
        ),
        migrations.AddField(
            model_name='comida',
            name='calorias',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
    ]
