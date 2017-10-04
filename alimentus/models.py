# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.db import models

# Create your models here.

class  Cliente(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE)
    sexo=(("M","Masculino"),
          ("F","Femenino"))
    doctor= models.ForeignKey(User, related_name='+',on_delete=models.CASCADE)
    genero = models.CharField(choices=sexo,max_length=1, blank=False, null=False)
    estatura = models.FloatField(null=False, blank=False)
    peso = models.FloatField(null=False, blank=False)
    diabetico = models.BooleanField(null=False, blank=False)

    def __unicode__(self):
        return self.user.get_username()


class Historico(models.Model):
    FechaHistorica = models.DateTimeField(primary_key=True)
    username = models.CharField(blank=True,null=True,max_length=60)
    estatura = models.FloatField(null=False, blank=False)
    peso = models.FloatField(null=False, blank=False)
    diabetico = models.BooleanField(null=False, blank=False)




class Cita(models.Model):
    paciente = models.ForeignKey(Cliente, on_delete=models.CASCADE )
    fecha_cita = models.DateField(default=timezone.now)

    def __unicode__(self):
        return self.paciente.user.get_username()+' ' + str(self.fecha_cita)






class Alimento(models.Model):
    Tipo_Alimento = (
        ("LA", "Lacteos"),
        ("HU", "Huevos"),
        ("CA", "Carnicos"),
        ("MA", "Pescados, moluscos, reptiles, crustaceos"),
        ("AC", "Grasas y Aceites"),
        ("CE", "Cereales"),
        ("LE", "Legumbres, semillas y frutos secos"),
        ("VE", "Verduras y Hortalizas"),
        ("FR", "Frutas"),
        ("AZ", "Azucar y Chocolates"),
        ("BE", "Bebidas"),
        ("MI", "Miscálenea"),
        ("PR", "Producto de uso nutricional")

    )
    nombre = models.CharField(max_length=100,unique=True)
    tipo = models.CharField(choices=Tipo_Alimento, max_length=2, blank=False, null=False)
    calorias = models.IntegerField(blank=False,null=False)
    grasa =models.FloatField(blank=False,null=False)
    proteina = models.FloatField(blank=False,null=False)
    agua = models.FloatField(blank=False,null=False)

    def __unicode__(self):
        return self.nombre

class Comida(models.Model):
    Tipo_Comida = (
        ("DE", "Desayuno"),
        ("CO", "Comida"),
        ("ME", "Merienda"),
        ("CE", "Cena")

    )

    fecha_comida = models.DateField(default=datetime.datetime.now)
    calorias =models.DecimalField(blank=False,null=False,max_digits=6,decimal_places=2,default=0)
    glucosa=models.IntegerField(blank=True,null=True)
    tipo = models.CharField(choices=Tipo_Comida,max_length=2,blank=False,null=False)
    paciente = models.ForeignKey(Cliente, on_delete=models.CASCADE,)
    alimentos = models.ManyToManyField(Alimento)
    def __unicode__(self):
        return str(self.fecha_comida)+  ' ' + self.paciente.user.get_username();








