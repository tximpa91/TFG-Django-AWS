# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import  *

# Register your models here.
class Admin (admin.ModelAdmin):
    list_display = ["__str__","user"]
    class Meta:
        models = Cliente


admin.site.register(Cliente,Admin)
admin.site.register(Alimento)
admin.site.register(Comida)
admin.site.register(Cita)
admin.site.register(Historico)










