# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django import forms
from .models import *
from choices import *


class SignInForm(forms.Form):
    username = forms.CharField(label="Username:", required=True, widget=forms.TextInput(attrs={'required': 'true'}))
    password = forms.CharField(label="Password:",required=True,widget=forms.PasswordInput(attrs={'required': 'true'}))

class Complete_Profile(ModelForm):
    doctor = forms.ModelChoiceField(required=True, queryset=User.objects.all().filter(is_staff=True),widget=forms.Select(attrs={'required': 'True', 'style': 'width:200px'}))
    genero = forms.ChoiceField(required=True, choices=sexo, widget=forms.Select(attrs={'style': 'width:200px'}))
    estatura = forms.DecimalField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Estatura', 'required': 'True,', 'type': 'number', 'style': 'width:80px', 'step': '0.01','min': '0', 'max': '2.50'}))
    peso = forms.DecimalField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Peso ', 'required': 'True,', 'type': 'number', 'style': 'width:75px', 'step': '0.01', 'min': '0', 'max': '500.00'}))
    diabetico = forms.BooleanField(required=False, label=" Diabetico", initial=False)

    class Meta:
        model = Cliente
        fields =['doctor','genero','estatura','peso','diabetico']



class SignUpForm(ModelForm):
    first_name = forms.CharField(required=True,label="Nombre:", widget=forms.TextInput(attrs={'style': 'width:200px','placeholder':'Nombre'}))
    last_name = forms.CharField(required=True,label="Apellidos:", widget=forms.TextInput(attrs={'style': 'width:200px','placeholder':'Apellido'}))
    email = forms.CharField(required=True,label='Email:',widget=forms.EmailInput( attrs={'style':'width:200px','placeholder':'Email'}))
    username= forms.CharField(required=True,label='Username:',widget=forms.TextInput(attrs={'style':'width:200px','placeholder':'Username','aria-describedby':'help-text'}))
    password = forms.CharField(required=True,label='Password:', widget=forms.PasswordInput(attrs={'style': 'width:200px','placeholder':'Password'}))
    re_password= forms.CharField(required=True,label='Re-Password:', widget=forms.PasswordInput(attrs={'style': 'width:200px','placeholder':'Re-password'}))
    doctor = forms.ModelChoiceField(required=True,queryset=User.objects.all().filter(is_staff=True),initial=1,widget=forms.Select(attrs={ 'required': 'True','style':'width:200px'}))
    genero = forms.ChoiceField(label='Género:',required=True,choices=sexo, widget=forms.Select(attrs={'style': 'width:200px'}))
    estatura = forms.DecimalField(required=True,widget=forms.TextInput(attrs={'placeholder':'Estatura','required':'True,','type': 'number','style': 'width:80px','step':'0.01','min':'0','max':'2.50'}))
    peso = forms.DecimalField(required=True,widget=forms.TextInput(attrs={'placeholder':'Peso ','required':'True,','type': 'number','style': 'width:75px','step':'0.01','min':'0','max':'500.00'}))
    diabetico = forms.BooleanField(required=False,label="Diabetico",initial=False)

    class Meta:
        model = Cliente
        fields = ['first_name', 'last_name', 'email','username','password','re_password','doctor','genero','estatura','peso','diabetico']

class InfoForm(ModelForm):
    first_name = forms.CharField(required=True,label="Nombre:", widget=forms.TextInput(attrs={'style': 'width:200px','placeholder':'Nombre'}))
    last_name = forms.CharField(required=True,label="Apellidos:", widget=forms.TextInput(attrs={'style': 'width:200px','placeholder':'Apellido'}))
    email = forms.CharField(required=True,label='Email:',widget=forms.EmailInput( attrs={'style':'width:200px','placeholder':'Email'}))
    username= forms.CharField(disabled=True,required=True,label='Username:',widget=forms.TextInput(attrs={'style':'width:200px','placeholder':'Username','aria-describedby':'help-text'}))
    doctor = forms.ModelChoiceField(required=True,queryset=User.objects.all().filter(is_staff=True),initial=1,widget=forms.Select(attrs={ 'required': 'True','style':'width:200px'}))
    genero = forms.ChoiceField(required=True,choices=sexo, widget=forms.Select(attrs={'style': 'width:200px'}))
    estatura = forms.DecimalField(required=True,widget=forms.TextInput(attrs={'placeholder':'Estatura','required':'True,','type': 'number','style': 'width:80px','step':'0.01','min':'0','max':'2.50'}))
    peso = forms.DecimalField(required=True,widget=forms.TextInput(attrs={'placeholder':'Peso ','required':'True,','type': 'number','style': 'width:75px','step':'0.01','min':'0','max':'500.00'}))
    diabetico = forms.BooleanField(required=False,label="Diabetico",initial=False)

    class Meta:
        model = Cliente
        fields = ['first_name', 'last_name', 'email','username','doctor','genero','estatura','peso','diabetico']


class AlimentoForm(ModelForm):
    nombre=forms.CharField(label="Nombre;",required=True,widget=forms.TextInput(attrs={'style':'width:200px', 'required': 'true','placeholder':'Nombre'}))
    tipo = forms.ChoiceField(required=True,label="Tipo:",choices=Tipo_Alimento,widget=forms.Select(attrs={'style': 'width:200px','placeholder':'Tipo'}))
    calorias = forms.IntegerField(label="Calorias",required=True,widget=forms.TextInput(attrs={'placeholder':'Calorias','required':'True,','type': 'number','style': 'width:80px','min':'0','max':'1000'}))
    grasa = forms.DecimalField(label="Grasa",required=True,widget=forms.TextInput(attrs={'placeholder':'Grasa','required':'True,','type': 'number','style': 'width:80px','step':'0.01','min':'0','max':'100'}))
    proteina = forms.DecimalField(label="Proteina",required=True,widget=forms.TextInput(attrs={'placeholder':'Proteina','required':'True,','type': 'number','style': 'width:80px','step':'0.01','min':'0','max':'100'}))
    agua = forms.DecimalField(label="Agua", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Agua', 'required': 'True,', 'type': 'number', 'style': 'width:80px', 'step': '0.01',
               'min': '0', 'max': '100'}))

    class Meta:
        model = Alimento
        fields =["nombre","tipo","calorias","grasa","proteina","agua"]


class PasswordResetRequestForm(forms.Form):
    username_password = forms.CharField( required=True,label='Username: ',widget=forms.TextInput( attrs={'style':'width:200px', 'required': 'true','aria-describedby':'id_username_password'}))

class Change_Password(forms.Form):
    password = forms.CharField(required=True,label='Password',widget=forms.PasswordInput(attrs={'style': 'width:200px'}))
    re_password =forms.CharField(required=True,label='Re-Password',widget=forms.PasswordInput(attrs={'style': 'width:200px'}))

class Semana(forms.Form):
    idSemana = forms.CharField(label="",required=False,widget=forms.TextInput(attrs={'style':'width:45px; height:20px; font-size: small;' }))
