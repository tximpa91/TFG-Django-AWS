# -*- coding: utf-8 -*-


# Create your views here.
import sys
from .forms import *
from django.contrib import auth
from django.http import JsonResponse
from .models import *
from datetime import date, timedelta, datetime
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.contrib.sites.models import Site
from django.db import IntegrityError
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from social_django.models import UserSocialAuth
import json
from django.utils.safestring import mark_safe
from django.contrib.auth import login as autenticar

def all_pacientes(request):
    pacient = []
    citas = []
    total_pacientes = 0
    resultados=[]
    pacientes = Cliente.objects.filter(doctor__username=request.user.get_username()).values("user__username",
                                                                                            "user__first_name",
                                                                                            "user__last_name",
                                                                                            "user__email", "peso",
                                                                                            "estatura", "diabetico")
    total_pacientes = len(pacientes)
    for instance in pacientes:
        pacient.append(instance)
        print instance.get("user__username")
        cantidad = Cita.objects.filter(paciente__user__username=instance.get("user__username")).count()
        citas.append(cantidad)

    list = zip(pacient, citas)
    resultados.append(list)
    resultados.append(total_pacientes)
    return resultados



def login(request):
    paciente_datos = False
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]


            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    request.session.set_expiry(0)
                    if user.is_staff:
                        resultados = all_pacientes(request)
                        return render(request, 'consulta_pacientes.html', {'queryset': resultados[0],
                                                                           'resultado': resultados[1]})
                    else:
                        try:
                            paciente = Cliente.objects.get(user=request.user)
                        except Cliente.DoesNotExist:
                            paciente = None

                            if paciente is None:
                                paciente_datos = True

                        form = Complete_Profile()
                    return render(request, 'home.html',
                                  {'user': request.user, 'paciente_datos': paciente_datos, 'form': form})
                else:
                    # An inactive account was used - no logging in!
                    mensaje = "Su cuenta esta deshabilitada por favor contacte al administrador"
                    messages.add_message(request, messages.ERROR, mensaje)
                    form = SignInForm()
                    form2 = PasswordResetRequestForm()
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    domains = str(Site.objects.get_current().domain + "/activate/" + uid + "/" + token)

                    html_message = loader.render_to_string(
                        '/opt/python/current/app/templates/activate_account.html',
                        {
                            'user_name': user.get_username(),
                            'link': domains
                        }
                    )



                    send_mail(
                        'Bienvenido',
                        None,
                        'food.control.uah@gmail.com',
                        [user.email],
                        fail_silently=True,

                        html_message=html_message,
                    )

                    return render(request, 'login.html', {'form': form,'form2':form2})
            else:
                mensaje = "Usuario o contraseña invalidos"
                messages.add_message(request, messages.ERROR, mensaje)
                form = SignInForm()
                form2 = PasswordResetRequestForm()

                return render(request, 'login.html', {'form': form,'form2':form2})

        else:
            mensaje = "Usuario o contraseña invalidos"
            messages.add_message(request, messages.ERROR, mensaje)

            form2 = PasswordResetRequestForm()

            return render(request, 'login.html', {'form': form, 'form2': form2})


    else:
        if request.user.is_authenticated():

            if request.session.get_expiry_age() < 0:
                print(request.session.get_expiry_age())
                auth.logout(request)
                log = SignInForm()
                form2 = PasswordResetRequestForm()
                mensaje = "Su cuenta esta deshabilitada por favor contacte al administrador"
                messages.add_message(request, messages.ERROR, mensaje)
                return render(request, 'login.html', {'form': log, 'form2': form2})
            if request.user.is_active is False:
                log = SignInForm()
                form2 = PasswordResetRequestForm()


                mensaje = "Su cuenta esta deshabilitada por favor contacte al administrador"
                messages.add_message(request, messages.ERROR, mensaje)
                return render(request, 'login.html', {'form': log, 'form2': form2})
            else:

                if request.user.is_staff:
                    resultados = all_pacientes(request)
                    return render(request, 'consulta_pacientes.html', {'queryset': resultados[0],
                                                                       'resultado': resultados[1]})

                else:
                    try:
                        paciente = Cliente.objects.get(user=request.user)
                    except Cliente.DoesNotExist:
                        paciente = None

                        if paciente is None:
                            paciente_datos = True

                    form = Complete_Profile()
                return render(request, 'home.html', {'user': request.user, 'paciente_datos': paciente_datos, 'form': form})

        else:
            form = SignInForm()
            form2 = PasswordResetRequestForm()

            return render(request, 'login.html', {'form': form,'form2':form2})



def signup(request):
    if request.method == 'POST':  # si ha sido sido pinchada pra registrar
        form = SignUpForm(request.POST)  # post
        if form.is_valid():
            email = form.cleaned_data["email"]
            username= form.cleaned_data["username"]
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            password = form.cleaned_data["password"]
            doc =form.cleaned_data["doctor"]
            peso= form.cleaned_data["peso"]
            estatura  = form.cleaned_data["estatura"]
            diabetico = form.cleaned_data["diabetico"]
            genero =form.cleaned_data["genero"]
            user =  User(username=username,email=email,first_name=first_name,last_name=last_name,password=password,is_active=False)

            try:
                user_doc = User.objects.get(username=doc)
            except User.DoesNotExist:
                user_doc = None
            if user_doc is not None:
                try:
                    user.save()
                except IntegrityError:
                    return render(request, 'signup.html', {'form': form})

                paciente = Cliente(user=user,doctor=user_doc,peso=peso,estatura=estatura,diabetico=diabetico,genero=genero)

                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                domains = str(Site.objects.get_current().domain + "/activate/" + uid + "/" + token)

                html_message = loader.render_to_string(
                    '/opt/python/current/app/templates/activate_account.html',
                    {
                        'user_name': user.get_username(),
                        'link': domains
                    }
                )

                paciente.save()

                send_mail(
                    'Bienvenido',
                    None,
                    'food.control.uah@gmail.com',
                    [user.email],
                    fail_silently=True,

                    html_message=html_message,
                )
                mensaje = "Gracias por registrarse, revise su correo: " + user.get_username() + ' para activar su cuenta'
                messages.add_message(request, messages.SUCCESS, mensaje)
                if request.user.is_authenticated() and request.user.is_staff:
                    resultados = all_pacientes(request)
                    return render(request, 'consulta_pacientes.html', {'queryset': resultados[0],
                                                                       'resultado': resultados[1]})



                form = SignInForm()
                form2 = PasswordResetRequestForm()

                return render(request, 'login.html', {'form': form, 'form2': form2})

            else:
                form2 = PasswordResetRequestForm()

                return render(request, 'login.html', {'form': form, 'form2': form2})
        else:

            form2 = PasswordResetRequestForm()

            return render(request, 'signup.html', {'form': form, 'form2': form2})



    else:

        form = SignUpForm()  # post
        form2 = PasswordResetRequestForm()
        return render(request, 'signup.html', {'form': form,'form2':form2})



def activate(request,uidb64,token):
    uid = urlsafe_base64_decode(uidb64)
    paciente_datos=False
    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        user = None
    if user is not None:
        if default_token_generator.check_token(user, token):
            user.is_active=True
            user.save()
            mensaje = "Bienvenido: " + user.get_username()
            messages.add_message(request, messages.SUCCESS, mensaje)
            try:
                paciente = Cliente.objects.get(user=user)
            except Cliente.DoesNotExist:
                paciente = None

                if paciente is None:
                    paciente_datos = True

            form = Complete_Profile()

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            autenticar(request, user)
            return render(request, 'home.html', {'user': user, 'paciente_datos': paciente_datos, 'form': form})
        else:
            mensaje = "Ha ocurrido un problema en autenticar su usuario"
            messages.add_message(request, messages.ERROR, mensaje)
            log = SignInForm()
            form2 = PasswordResetRequestForm()

            return render(request, 'login.html', {'form': log, 'form2': form2})

    else:
        mensaje = "Ha ocurrido un problema en autenticar su usuario"
        messages.add_message(request, messages.ERROR, mensaje)
        log = SignInForm()
        form2 = PasswordResetRequestForm()

        return render(request, 'login.html', {'form': log, 'form2': form2})



def reset(request):
    if request.method=='POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            username= form.cleaned_data["username_password"]
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None
            try:
                social = UserSocialAuth.objects.get(user_id=user.id)
            except UserSocialAuth.DoesNotExist:
                social = None

            if user is not None and social is None :
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                uid_date = urlsafe_base64_encode(force_bytes(datetime.today()))

                domains = str(Site.objects.get_current().domain + "/reset_confirm/" + uid + "/" +uid_date )
                html_message = loader.render_to_string(
                    '/opt/python/current/app/templates/password_reset_email.html',
                    {
                        'user_name': user.get_username(),
                        'link': domains
                    }
                )

                send_mail(
                    'Reestablecer Contraseña',
                    None,
                    'food.control.uah@gmail.com',
                    [user.email],
                    fail_silently=True,

                    html_message=html_message,
                )
                mensaje = "Se ha enviado un correo con las instrucciones para reestablecer su contraseña"
                messages.add_message(request, messages.SUCCESS, mensaje)
                log = SignInForm()
                form2 = PasswordResetRequestForm()

                return render(request, 'login.html', {'form': log, 'form2': form2})

            else:
                if user is None:
                    mensaje = "Usuario no existe"
                elif social is not None:
                    mensaje = "Su cuenta fue creada a traves de redes sociales esta opción es invalida"

                messages.add_message(request, messages.ERROR, mensaje)
                log = SignInForm()
                form2 = PasswordResetRequestForm()
                return render(request, 'login.html', {'form': log, 'form2': form2})



    else:

        log = SignInForm()
        form2 = PasswordResetRequestForm()
        return render(request, 'login.html', {'form': log, 'form2': form2})

def change_password(request):
    if request.method == 'POST':

        username = request.POST["username"]
        password= request.POST["password"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user is not None:
            user.set_password(password)
            user.save()
            mensaje = "Su Contraseña ha sido reestablecida "
            messages.add_message(request, messages.SUCCESS, mensaje)
            log = SignInForm()
            form2 = PasswordResetRequestForm()

            return render(request, 'login.html', {'form': log, 'form2': form2})


def reset_confirm(request,uidb64,uidb65):
        uid = urlsafe_base64_decode(uidb64)
        date =urlsafe_base64_decode(uidb65)
        url_date= datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        actual_date = datetime.today()
        valid_link = (actual_date - url_date).total_seconds()
        if valid_link <= 60*15 :
            try:
                user = User.objects.get(pk=uid)
            except User.DoesNotExist:
                user = None
            log = Change_Password()
            return render(request, 'password_reset_confirm.html', {'form': log, 'username':user.get_username()})
        else:
            mensaje = "Este link ya no es válido  "
            messages.add_message(request, messages.ERROR, mensaje)
            log = SignInForm()
            form2 = PasswordResetRequestForm()
            return render(request, 'login.html', {'form': log, 'form2': form2})



def validate_username(request):
    if request.method == 'POST':
        username = request.POST["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user is not None:
            data = {
                'is_taken': True
            }

        else:
            data = {
                'is_taken': False
            }
        return JsonResponse(data)


@login_required()
def home(request):
    paciente_datos=False
    if request.session.get_expiry_age() < 0:
        print(request.session.get_expiry_age())
        auth.logout(request)
        log = SignInForm()
        form2 = PasswordResetRequestForm()
        mensaje = "Su cuenta esta deshabilitada por favor contacte al administrador"
        messages.add_message(request, messages.ERROR, mensaje)
        return render(request, 'login.html', {'form': log, 'form2': form2})
    if request.user.is_active is False:
        log = SignInForm()
        form2 = PasswordResetRequestForm()
        mensaje = "Su cuenta esta deshabilitada por favor contacte al administrador"
        messages.add_message(request, messages.ERROR, mensaje)
        return render(request, 'login.html', {'form': log, 'form2': form2})
    else:
        if request.user.is_staff:
            resultados = all_pacientes(request)
            return render(request, 'consulta_pacientes.html', {'queryset': resultados[0],
                                                               'resultado': resultados[1]})
        else:
            try:
                paciente = Cliente.objects.get(user=request.user)
            except Cliente.DoesNotExist:
                paciente = None

                if paciente is None:
                    paciente_datos = True

            form = Complete_Profile()
        return render(request, 'home.html', {'user': request.user,'paciente_datos':paciente_datos,'form':form})

@login_required
def log_out(request):
    try:
        twitter_login = request.user.social_auth.get(provider='twitter')
    except UserSocialAuth.DoesNotExist:
        twitter_login = None

    try:
        facebook_login = request.user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    try:
        google_login = request.user.social_auth.get(provider='google-oauth2')
    except UserSocialAuth.DoesNotExist:
        google_login = None

    auth.logout(request)


    return render(request, 'logout.html', {

    })


@login_required()
def complete_profile(request):
    paciente_datos=False
    if request.method=='POST':
        form = Complete_Profile(request.POST)
        if form.is_valid():
            doc = form.cleaned_data["doctor"]
            peso = form.cleaned_data["peso"]
            estatura = form.cleaned_data["estatura"]
            diabetico = form.cleaned_data["diabetico"]
            genero = form.cleaned_data["genero"]
            try:
                user_doc = User.objects.get(username=doc)
            except User.DoesNotExist:
                user_doc = None

            if user_doc is not None:
                paciente = Cliente(user=request.user, doctor=user_doc, peso=peso, estatura=estatura, diabetico=diabetico,
                               genero=genero)

                paciente.save()
                return render(request, 'home.html',
                              {'user': request.user, 'paciente_datos': paciente_datos})

    else:
        try:
            paciente = Cliente.objects.get(user=request.user)
        except Cliente.DoesNotExist:
            paciente = None

            if paciente is None:
                paciente_datos = True

            form = Complete_Profile()
    return render(request, 'home.html', {'user': request.user,'paciente_datos':paciente_datos,'form':form})

@login_required()
def eliminar_citas(request):
    if request.method == 'POST':
        citas_eliminadas = request.POST["citas_eliminadas"]
        citas_clientes_eliminadas = json.loads(citas_eliminadas)
        for e in citas_clientes_eliminadas:
            fecha_aux = datetime.strptime(e.get("start"), "%Y-%m-%d").date()
            fecha_tz_ini = datetime(fecha_aux.year, fecha_aux.month, fecha_aux.day)
            try:
                delete_cita = Cita.objects.get(paciente__user__username=e.get("title"), fecha_cita=fecha_tz_ini)
            except Cita.DoesNotExist:
                delete_cita = None

            if delete_cita is not None:
                delete_cita.delete()

        data = {
            'is_delete': True
        }
        return JsonResponse(data)

@login_required()
def citas(request,username):
    lista_pacientes=[]
    listal=[]
    control = False

    if request.method == 'POST':
        citas = request.POST["citas"]
        citas_eliminadas=request.POST["citas_eliminadas"]
        citas_clientes_eliminadas = json.loads(citas_eliminadas)
        citas_clientes =json.loads(citas)

        for e in citas_clientes_eliminadas:
            fecha_aux = datetime.strptime(e.get("start"), "%Y-%m-%d").date()
            fecha_tz_ini = datetime(fecha_aux.year, fecha_aux.month, fecha_aux.day)
            try:
                delete_cita = Cita.objects.get(paciente__user__username=e.get("title") ,fecha_cita=fecha_tz_ini)
            except Cita.DoesNotExist:
                delete_cita = None

            if delete_cita is not None:
                delete_cita.delete()


        for o in citas_clientes:

           fecha_aux=datetime.strptime(o.get("start"), "%Y-%m-%d").date()
           fecha_tz_ini = datetime(fecha_aux.year, fecha_aux.month, fecha_aux.day)
           len_citas= Cita.objects.filter(fecha_cita=fecha_tz_ini)
           if len(len_citas) < 8:
               try:
                   update_cita = Cita.objects.get(paciente__user__username=o.get("title"),fecha_cita= fecha_tz_ini)
               except Cita.DoesNotExist:
                   update_cita = None

               if update_cita is None:
                   new_cita = Cita(paciente=get_user(o.get("title")),fecha_cita=fecha_tz_ini)
                   new_cita.save()
                   doc = (get_doc((get_user(o.get("title")).doctor.get_username())))


                   html_message = loader.render_to_string(
                     '/opt/python/current/app/templates/recordatorio_cita.html',
                       {
                           'user_name': new_cita.paciente.user.get_username(),
                           'doctor': doc.first_name + ' ' + doc.last_name,
                           'fecha' : fecha_tz_ini.date()

                       }
                   )
                   send_mail(
                       'Ha programado una nueva cita',
                       None,
                       'food.control.uah@gmail.com',
                       [new_cita.paciente.user.email],
                       fail_silently=False,

                       html_message=html_message,
                   )
                   mensaje = 'Sus cambios se realizaron correctamente  '

                   messages.add_message(request, messages.SUCCESS, mensaje)
 #              else:
 #                  print o.get("end")
 #                  if o.geapt("end") == 'true':
 #                      if request.user.is_staff:
 #                          mensaje = 'Ya tiene citas programada para las fechas: '
 #                      else:
 #                          mensaje = 'El paciente ya tiene citas programas para la fechas: \n'
#
#                       mensaje = mensaje + str(fecha_tz_ini.date())

#                       messages.add_message(request, messages.SUCCESS, mensaje)
           else:
               mensaje = 'No se permiten mas de 8 citas por día, revise su calendario'
               messages.add_message(request, messages.ERROR, mensaje)


        citas = Cita.objects.none()
        if request.user.is_staff:
            pacientes = Cliente.objects.filter(doctor__username=request.user.get_username())

        else:
            pacientes = Cliente.objects.filter(user__exact=request.user)

        for instance in pacientes:
            lista_pacientes.append(instance)
            citas = citas | Cita.objects.filter(paciente__user__username__contains=instance).order_by(
                '-fecha_cita').values(
                "paciente__user__username", "fecha_cita")
        for instance in citas:
            listal.append(instance)


        return render(request, "citas.html",
                      {
                          'semana_imputacion': listal, 'pacientes': lista_pacientes, 'paciente': username})



    else:
        citas = Cita.objects.none()
        if request.user.is_staff:
            pacientes = Cliente.objects.filter(doctor__username=request.user.get_username())
        else:
            pacientes = Cliente.objects.filter(user__exact=request.user)


        for instance in pacientes:
            lista_pacientes.append(instance)
            citas = citas | Cita.objects.filter(paciente__user__username=instance).order_by('-fecha_cita').values(
                "paciente__user__username", "fecha_cita")
        for instance in citas:
            listal.append(instance)

        return render(request, "citas.html",
                      {
                          'semana_imputacion': listal, 'pacientes': lista_pacientes,'paciente': username})

def dias_semana(week):
    week_aux = date.today().isocalendar()[1]
    queryweek = []
    if week > week_aux:
        week = week - week_aux
        fecha = date.today() + timedelta(weeks=week)
        auxiliar = fecha.weekday()
        if auxiliar == 0:
            dias_inicio = fecha.isoformat()
            queryweek.append(None)
            queryweek.append(fecha)
            for i in range(1, 7):
                fecha_aux = (dias_inicio + timedelta(days=i))
                queryweek.append(fecha_aux)
            return queryweek

        else:
            dias_inicio = fecha - timedelta(days=fecha.weekday())
            queryweek.append(None)
            queryweek.append(dias_inicio)
            for i in range(1, 7):
                fecha_aux = (dias_inicio + timedelta(days=i))
                queryweek.append(fecha_aux)
            return queryweek


    elif week < week_aux:
        week = week_aux - week

        fecha = date.today() - timedelta(weeks=week)

        auxiliar = fecha.weekday()

        if auxiliar == 0:

            dias_inicio = fecha.isoformat()

            queryweek.append(None)
            queryweek.append(fecha)
            for i in range(1, 7):
                fecha_aux = (dias_inicio + timedelta(days=i))
                queryweek.append(fecha_aux)
            return queryweek
        else:

            dias_inicio = fecha - timedelta(days=fecha.weekday())
            dias_final = dias_inicio + timedelta(days=6)
            queryweek.append(None)
            queryweek.append(dias_inicio)
            for i in range(1, 7):
                fecha_aux = (dias_inicio + timedelta(days=i))
                queryweek.append(fecha_aux)
            return queryweek
    else:
        fecha = date.today()
        auxiliar = fecha.weekday()
        if auxiliar == 0:

            dias_inicio = fecha.isoformat()
            queryweek.append(None)
            queryweek.append(fecha)
            for i in range(1, 7):
                fecha_aux = (dias_inicio + timedelta(days=i))
                print(fecha)
                queryweek.append(fecha_aux)
            return queryweek
        else:

            dias_inicio = fecha - timedelta(days=fecha.weekday())
            dias_final = dias_inicio + timedelta(days=6)
            queryweek.append(None)
            queryweek.append(dias_inicio)
            for i in range(1, 7):
                fecha_aux = (dias_inicio + timedelta(days=i))
                print(fecha_aux)
                queryweek.append(fecha_aux)
            return queryweek


def verano_2(fecha):
    dia = fecha.day

    mes = fecha.month

    if (dia >= 21 and mes == 6) or (mes >= 7 and mes <= 9):
        return True
    else:
        return False

@login_required()
def signup_doctor(request):
    if request.user.is_staff:
        if request.method == 'POST':  # si ha sido sido pinchada pra registrar
            form = SignUpForm(request.POST)  # post
            if form.is_valid():
                email = form.cleaned_data["email"]
                username= form.cleaned_data["username"]
                first_name=form.cleaned_data["first_name"]
                last_name=form.cleaned_data["last_name"]
                password = form.cleaned_data["password"]
                doc =form.cleaned_data["doctor"]
                peso= form.cleaned_data["peso"]
                estatura  = form.cleaned_data["estatura"]
                diabetico = form.cleaned_data["diabetico"]
                genero =form.cleaned_data["genero"]
                user =  User(username=username,email=email,first_name=first_name,last_name=last_name,password=password,is_active=False)

                try:
                    user_doc = User.objects.get(username=doc)
                except User.DoesNotExist:
                    user_doc = None
                if user_doc is not None:
                    try:
                        user.save()
                    except IntegrityError:
                        return render(request, 'signup.html', {'form': form})

                    paciente = Cliente(user=user,doctor=user_doc,peso=peso,estatura=estatura,diabetico=diabetico,genero=genero)

                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    domains = str(Site.objects.get_current().domain + "/activate/" + uid + "/" + token)

                    html_message = loader.render_to_string(
                        str(sys.path[0]) + '/templates/activate_account.html',
                        {
                            'user_name': user.get_username(),
                            'link': domains
                        }
                    )

                    paciente.save()

                    send_mail(
                        'Bienvenido',
                        None,
                        'food.control.uah@gmail.com',
                        [user.email],
                        fail_silently=True,

                        html_message=html_message,
                    )

                    form = Complete_Profile()
                    return render(request, 'home.html',
                                  {'user': request.user, 'paciente_datos': False, 'form': form})

                else:
                    form = Complete_Profile()
                    return render(request, 'home.html',
                                  {'user': request.user, 'paciente_datos': False, 'form': form})
            else:

                form2 = PasswordResetRequestForm()

                return render(request, 'signup.html', {'form': form, 'form2': form2})



        else:

            form = SignUpForm()
            form.fields['doctor'].queryset=User.objects.filter(username=request.user)


            form2 = PasswordResetRequestForm()
            return render(request, 'signup.html', {'form': form,'form2':form2})


@login_required()
def crear_alimento(request):
    if request.method=='POST':
        form = AlimentoForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data["nombre"]
            tipo   = form.cleaned_data["tipo"]
            proteina = form.cleaned_data["proteina"]
            calorias =  form.cleaned_data["calorias"]
            grasa = form.cleaned_data["grasa"]
            agua  = form.cleaned_data["agua"]

            alimento = Alimento(nombre=nombre,tipo=tipo,calorias=calorias,proteina=proteina,grasa=grasa,agua=agua)

            try:
                alimento.save()
            except IntegrityError:
                mensaje = 'El Alimento ya existe'
                messages.add_message(request, messages.SUCCESS, mensaje)
                return render(request, 'alimento.html', {'form': form})
            resultados = all_pacientes(request)
            return render(request, 'consulta_pacientes.html', {'queryset': resultados[0],
                                                               'resultado': resultados[1]})
        else:
            return render(request, 'alimento.html', {'form': form})
    else:
        form = AlimentoForm()
        return render(request, 'alimento.html', {'form': form, })

@login_required()
def personal_info(request):
    if request.method=='POST':
        form = InfoForm(request.POST)
        cliente = get_user(request.user.get_username())
        cliente.user.first_name = form.data["first_name"]
        cliente.user.last_name = form.data["last_name"]
        cliente.user.email = form.data["email"]

        try:
            doctor = User.objects.get(id=form.data["doctor"])
        except User.DoesNotExist:
            doctor = None
        if doctor is not None:
            cliente.doctor = doctor
            cliente.diabetico = form.data["diabetico"]

        cliente.user.save()
        cliente.save()
        mensaje='Sus datos fueron modificados correctamente'
        messages.add_message(request, messages.SUCCESS, mensaje)


        return render(request, 'home.html')
    else:
        cliente = get_user(request.user.get_username())
        form = InfoForm(instance=request.user,
                        initial={"estatura":cliente.estatura,
                                 "peso":cliente.peso,
                                 "diabetico":cliente.diabetico,
                                 "doctor":User.objects.filter(is_staff=True),
                                 })
        return  render(request, 'informacion.html', {'form': form })


def get_user(username):
    try:
        user =Cliente.objects.get(user__username=username)
    except Cliente.DoesNotExist:
        user = None

    return  user

def get_doc(username):
    try:
        user =User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    return  user

def get_food(id):
    try:
        alimento = Alimento.objects.get(id=id)
    except Alimento.DoesNotExist:
        alimento = None
    return alimento


@login_required()
def busca_pacientes(request):
    if request.method=='POST':
        resultados = all_pacientes(request)
    else:
        resultados = all_pacientes(request)

    return render(request, 'consulta_pacientes.html', {'queryset': resultados[0],
                                                       'resultado': resultados[1]})

@login_required()
def tipo_comida(request):

    if request.method=='POST':
        eleccion =request.POST["eleccion"]
        diabetico = get_user(request.user.get_username()).diabetico
        return render(request, 'registrar_comida.html',{'eleccion': eleccion, 'diabetico':diabetico})
    else:

        return render(request,'tipo_comida.html')


@login_required()
def registrar_comida(request,tipo):
    gramos=0
    calorias =0
    diabetico = get_user(request.user.get_username()).diabetico
    if request.method=='POST':
        web_flow = request.POST["menu"]
        diabetico = request.POST["glucosa"]
        alimentos = request.POST["alimentos"]
        alimentos_seleccionados = json.loads(alimentos)
        comida = Comida(paciente=get_user(request.user.get_username()),
                        tipo=(tipo[:2]).upper(),
                        glucosa=int(diabetico))
        comida.save()
        mensaje = '<i> Su comida fue correctamente registrada  <br> '
        for object in alimentos_seleccionados:
            gramos = float(object.get("gramos"))
            food = get_food(object.get("id"))

            if (gramos != 100):
                calorias= calorias +((food.calorias * gramos)/100)

            else:
                calorias = calorias + food.calorias



            comida.alimentos.add(food)
        comida.calorias=calorias

        mensaje = mensaje + 'Calorias totales: ' + str(calorias) + '</i>'

        comida.save()

        messages.add_message(request, messages.SUCCESS, mensaje)
        print "glucosa" + (diabetico)

        if (web_flow=='true'):
            return render(request, 'tipo_comida.html')
        else:
            return render(request, 'home.html')




    else:
        return render(request, 'registrar_comida.html',{'eleccion':tipo,'diabetico':diabetico})


@login_required()
def query_alimentos(request):
    alimentos= []
    eleccion =request.POST["comida"]



    queryset_alimento = Alimento.objects.filter(tipo=eleccion)

    for instance in queryset_alimento:
        object={'text': instance.nombre,

                'id':instance.id


        }
        alimentos.append(object)

    return JsonResponse (alimentos, safe=False)

@login_required()
def progress_charts(request,username):
    username = get_doc(username)
    listal = []
    lista_glucosa=[]
    queryweek = []
    calorias=0
    glucosa =0
    diabetes = False
    glucosa_global=0
    semana_literal=['Lunes','Martes','Miercoles','Jueves','Viernes','Sabado','Domingo']
    if request.method == 'POST' and 'avanzar' in request.POST:
        week = request.POST["week"]
        week = int(week) + 1
        fecha = date.today() + timedelta(weeks=(week - date.today().isocalendar()[1]))
        semana = week
        auxiliar = fecha.weekday()
        form = Semana(initial={'idSemana': semana})
        user = request.user
        if auxiliar == 0:
            dias_inicio = fecha
            dias_final = fecha + timedelta(days=6)
            dias_final = dias_final.isoformat()
            for i in range(0, 7):
                fecha_aux = (dias_inicio + timedelta(days=i))
                query_set = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username().get_username() )
                veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username(),
                                              glucosa__gt=0).count()
                if veces is 0:
                    veces = 1;
                for instance in query_set:
                    calorias = calorias + instance.calorias;
                    glucosa = glucosa + instance.glucosa;

                data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day) , 'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                listal.append(data)
                calorias = 0
                data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                        'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                lista_glucosa.append(data_glucosa)
                glucosa_global=glucosa_global +glucosa;
                glucosa=0

            if glucosa_global >0:
                diabetes= True;

            dias_inicio = dias_inicio.isoformat()
            row_json = mark_safe(json.dumps(listal))
            row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

            return render(request, "charts.html",
                          {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final, 'diabetes': diabetes,
                           'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                           })


        else:

            dias_inicio = fecha - timedelta(days=fecha.weekday())
            dias_final = dias_inicio + timedelta(days=6)
            dias_final = dias_final.isoformat()

            for i in range(0, 7):
                fecha_aux = (dias_inicio + timedelta(days=i))
                queryweek.append(fecha_aux.day)
                query_set = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username())
                veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                              paciente__user__username=username.get_username(),
                                              glucosa__gt=0).count()
                if veces is 0:
                    veces = 1;

                for instance in query_set:
                    calorias = calorias + instance.calorias;
                    glucosa = glucosa + instance.glucosa;

                data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                        'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                listal.append(data)
                calorias = 0
                data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                                'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                lista_glucosa.append(data_glucosa)
                glucosa_global = glucosa_global + glucosa;
                glucosa = 0

            if glucosa_global > 0:
                diabetes = True;

            dias_inicio = dias_inicio.isoformat()
            row_json = mark_safe(json.dumps(listal))
            row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

            return render(request, "charts.html",
                          {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final, 'diabetes': diabetes,
                           'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                           })


    elif request.method == 'POST' and 'retroceder' in request.POST:
        week = request.POST["week"]
        week = int(week) - 1
        if week is 0:
            queryweek = []
            fecha = date.today()
            semana = fecha.isocalendar()[1]
            ########################################### calculo de los días de la semana correspondiente
            auxiliar = fecha.weekday()
            form = Semana(initial={'idSemana': semana})
            user = request.user


            if auxiliar == 0:
                listal = []
                horas = None
                lista_idTarea = []
                dias_inicio = fecha.isoformat()
                dias_final = fecha + timedelta(days=6)
                dias_final = dias_final.isoformat()

                for i in range(0, 7):
                    fecha_aux = (dias_inicio + timedelta(days=i))
                    queryweek.append(fecha_aux.day)
                    query_set = Comida.objects.filter(fecha_comida=fecha_aux,
                                                      paciente__user__username=username.get_username())
                    veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username(),
                                                  glucosa__gt=0).count()
                    if veces is 0:
                        veces = 1;

                    for instance in query_set:
                        calorias = calorias + instance.calorias;
                        glucosa = glucosa + instance.glucosa;

                    data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                            'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                    listal.append(data)
                    calorias = 0
                    data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                                    'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                    lista_glucosa.append(data_glucosa)
                    glucosa_global = glucosa_global + glucosa;
                    glucosa = 0

                if glucosa_global > 0:
                    diabetes = True;

                dias_inicio = dias_inicio.isoformat()
                row_json = mark_safe(json.dumps(listal))
                row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

                return render(request, "charts.html",
                              {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final,
                               'diabetes': diabetes,
                               'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                               })

            else:
                dias_inicio = fecha - timedelta(days=fecha.weekday())
                dias_final = dias_inicio + timedelta(days=6)
                dias_final = dias_final.isoformat()

                for i in range(0, 7):
                    fecha_aux = (dias_inicio + timedelta(days=i))
                    queryweek.append(fecha_aux.day)
                    query_set = Comida.objects.filter(fecha_comida=fecha_aux,
                                                      paciente__user__username=username.get_username())
                    veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username(),
                                                  glucosa__gt=0).count()
                    if veces is 0:
                        veces = 1;

                    for instance in query_set:
                        calorias = calorias + instance.calorias;
                        glucosa = glucosa + instance.glucosa;

                    data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                            'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                    listal.append(data)
                    calorias = 0
                    data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                                    'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                    lista_glucosa.append(data_glucosa)
                    glucosa_global = glucosa_global + glucosa;
                    glucosa = 0

                if glucosa_global > 0:
                    diabetes = True;

                dias_inicio = dias_inicio.isoformat()
                row_json = mark_safe(json.dumps(listal))
                row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

                return render(request, "charts.html",
                              {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final,
                               'diabetes': diabetes,
                               'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                               })

        else:

            fecha = date.today() - timedelta(weeks=(date.today().isocalendar()[1] - week))
            semana = week
            auxiliar = fecha.weekday()
            form = Semana(initial={'idSemana': semana})
            user = request.user


            if auxiliar == 0:
                listal = []
                horas = None
                lista_idTarea = []
                dias_inicio = fecha
                dias_final = fecha + timedelta(days=6)
                dias_final = dias_final.isoformat()

                for i in range(0, 7):
                    fecha_aux = (dias_inicio + timedelta(days=i))
                    queryweek.append(fecha_aux.day)
                    query_set = Comida.objects.filter(fecha_comida=fecha_aux,
                                                      paciente__user__username=username.get_username())
                    veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username(),
                                                  glucosa__gt=0).count()
                    if veces is 0:
                        veces = 1;

                    for instance in query_set:
                        calorias = calorias + instance.calorias;
                        glucosa = glucosa + instance.glucosa;

                    data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                            'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                    listal.append(data)
                    calorias = 0
                    data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                                    'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                    lista_glucosa.append(data_glucosa)
                    glucosa_global = glucosa_global + glucosa;
                    glucosa = 0

                if glucosa_global > 0:
                    diabetes = True;

                dias_inicio = dias_inicio.isoformat()
                row_json = mark_safe(json.dumps(listal))
                row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

                return render(request, "charts.html",
                              {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final,
                               'diabetes': diabetes,
                               'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                               })

            else:
                dias_inicio = fecha - timedelta(days=fecha.weekday())
                dias_final = dias_inicio + timedelta(days=6)
                dias_final = dias_final.isoformat()

                for i in range(0, 7):
                    fecha_aux = (dias_inicio + timedelta(days=i))
                    queryweek.append(fecha_aux.day)
                    query_set = Comida.objects.filter(fecha_comida=fecha_aux,
                                                      paciente__user__username=username.get_username())
                    veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username(),
                                                  glucosa__gt=0).count()
                    if veces is 0:
                        veces = 1;

                    for instance in query_set:
                        calorias = calorias + instance.calorias;
                        glucosa = glucosa + instance.glucosa;

                    data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                            'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                    listal.append(data)
                    calorias = 0
                    data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                                    'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                    lista_glucosa.append(data_glucosa)
                    glucosa_global = glucosa_global + glucosa;
                    glucosa = 0

                if glucosa_global > 0:
                    diabetes = True;

                dias_inicio = dias_inicio.isoformat()
                row_json = mark_safe(json.dumps(listal))
                row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

                return render(request, "charts.html",
                              {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final,
                               'diabetes': diabetes,
                               'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                               })


    elif request.method == 'POST' and 'ir_a' in request.POST:
        week = int(request.POST["week"])
        week_aux = date.today().isocalendar()[1]
        queryweek = []
        semana = week

        if week > week_aux:
            week = week - week_aux
            fecha = date.today() + timedelta(weeks=week)
            auxiliar = fecha.weekday()
            form = Semana(initial={'idSemana': semana})
            user = request.user
            print ("aqui_2")

            if auxiliar == 0:
                listal = []
                horas = None
                lista_idTarea = []
                dias_inicio = fecha.isoformat()
                dias_final = fecha + timedelta(days=6)
                dias_final = dias_final.isoformat()

                for i in range(0, 7):
                    fecha_aux = (dias_inicio + timedelta(days=i))
                    queryweek.append(fecha_aux.day)
                    query_set = Comida.objects.filter(fecha_comida=fecha_aux,
                                                      paciente__user__username=username.get_username())
                    veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username(),
                                                  glucosa__gt=0).count()
                    if veces is 0:
                        veces = 1;

                    for instance in query_set:
                        calorias = calorias + instance.calorias;
                        glucosa = glucosa + instance.glucosa;

                    data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                            'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                    listal.append(data)
                    calorias = 0
                    data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                                    'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                    lista_glucosa.append(data_glucosa)
                    glucosa_global = glucosa_global + glucosa;
                    glucosa = 0

                if glucosa_global > 0:
                    diabetes = True;

                dias_inicio = dias_inicio.isoformat()
                row_json = mark_safe(json.dumps(listal))
                row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

                return render(request, "charts.html",
                              {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final,
                               'diabetes': diabetes,
                               'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                               })


            else:

                listal = []
                horas = None
                lista_idTarea = []

                dias_inicio = fecha - timedelta(days=fecha.weekday())
                dias_final = dias_inicio + timedelta(days=6)
                dias_final = dias_final.isoformat()

                for i in range(0, 7):
                    fecha_aux = (dias_inicio + timedelta(days=i))
                    queryweek.append(fecha_aux.day)
                    query_set = Comida.objects.filter(fecha_comida=fecha_aux,
                                                      paciente__user__username=username.get_username())
                    veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username(),
                                                  glucosa__gt=0).count()
                    if veces is 0:
                        veces = 1;

                    for instance in query_set:
                        calorias = calorias + instance.calorias;
                        glucosa = glucosa + instance.glucosa;

                    data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                            'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                    listal.append(data)
                    calorias = 0
                    data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                                    'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                    lista_glucosa.append(data_glucosa)
                    glucosa_global = glucosa_global + glucosa;
                    glucosa = 0

                if glucosa_global > 0:
                    diabetes = True;

                dias_inicio = dias_inicio.isoformat()
                row_json = mark_safe(json.dumps(listal))
                row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

                return render(request, "charts.html",
                              {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final,
                               'diabetes': diabetes,
                               'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                               })


        elif week < week_aux:
            week = week_aux - week
            print(week)
            fecha = date.today() - timedelta(weeks=week)
            print("---------------------", fecha.isocalendar()[1])
            auxiliar = fecha.weekday()
            form = Semana(initial={'idSemana': semana})
            user = request.user


            if auxiliar == 0:

                dias_inicio = fecha
                dias_final = fecha + timedelta(days=6)
                dias_final = dias_final.isoformat()

                for i in range(0, 7):
                    fecha_aux = (dias_inicio + timedelta(days=i))
                    queryweek.append(fecha_aux.day)
                    query_set = Comida.objects.filter(fecha_comida=fecha_aux,
                                                      paciente__user__username=username.get_username())
                    veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username(),
                                                  glucosa__gt=0).count()
                    if veces is 0:
                        veces=1


                    for instance in query_set:
                        calorias = calorias + instance.calorias;
                        glucosa = glucosa + instance.glucosa;

                    data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                            'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                    listal.append(data)
                    calorias = 0
                    data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                                    'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                    lista_glucosa.append(data_glucosa)
                    glucosa_global = glucosa_global + glucosa;
                    glucosa = 0

                if glucosa_global > 0:
                    diabetes = True;

                dias_inicio = dias_inicio.isoformat()
                row_json = mark_safe(json.dumps(listal))
                row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

                return render(request, "charts.html",
                              {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final,
                               'diabetes': diabetes,
                               'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                               })

            else:

                dias_inicio = fecha - timedelta(days=fecha.weekday())
                dias_final = dias_inicio + timedelta(days=6)
                dias_final = dias_final.isoformat()

                for i in range(0, 7):
                    fecha_aux = (dias_inicio + timedelta(days=i))
                    queryweek.append(fecha_aux.day)
                    query_set = Comida.objects.filter(fecha_comida=fecha_aux,
                                                      paciente__user__username=username.get_username())
                    veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username(),
                                                  glucosa__gt=0).count()
                    if veces is 0:
                        veces = 1;

                    for instance in query_set:
                        calorias = calorias + instance.calorias;
                        glucosa = glucosa + instance.glucosa;

                    data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                            'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                    listal.append(data)
                    calorias = 0
                    data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                                    'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                    lista_glucosa.append(data_glucosa)
                    glucosa_global = glucosa_global + glucosa;
                    glucosa = 0

                if glucosa_global > 0:
                    diabetes = True;

                dias_inicio = dias_inicio.isoformat()
                row_json = mark_safe(json.dumps(listal))
                row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

                return render(request, "charts.html",
                              {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final,
                               'diabetes': diabetes,
                               'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                               })

        else:
            fecha = date.today()
            auxiliar = fecha.weekday()
            form = Semana(initial={'idSemana': semana})
            user = request.user


            if auxiliar == 0:

                dias_inicio = fecha
                dias_final = fecha + timedelta(days=6)
                dias_final = dias_final.isoformat()

                for i in range(0, 7):
                    fecha_aux = (dias_inicio + timedelta(days=i))
                    queryweek.append(fecha_aux.day)
                    query_set = Comida.objects.filter(fecha_comida=fecha_aux,
                                                      paciente__user__username=username.get_username())
                    veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username(),
                                                  glucosa__gt=0).count()
                    if veces is 0:
                        veces = 1;

                    for instance in query_set:
                        calorias = calorias + instance.calorias;
                        glucosa = glucosa + instance.glucosa;

                    data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                            'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                    listal.append(data)
                    calorias = 0
                    data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                                    'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                    lista_glucosa.append(data_glucosa)
                    glucosa_global = glucosa_global + glucosa;
                    glucosa = 0

                if glucosa_global > 0:
                    diabetes = True;

                dias_inicio = dias_inicio.isoformat()
                row_json = mark_safe(json.dumps(listal))
                row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

                return render(request, "charts.html",
                              {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final,
                               'diabetes': diabetes,
                               'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                               })

            else:

                dias_inicio = fecha - timedelta(days=fecha.weekday())
                dias_final = dias_inicio + timedelta(days=6)
                dias_final = dias_final.isoformat()

                for i in range(0, 7):
                    fecha_aux = (dias_inicio + timedelta(days=i))
                    queryweek.append(fecha_aux.day)
                    query_set = Comida.objects.filter(fecha_comida=fecha_aux,
                                                      paciente__user__username=username.get_username())
                    veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username(),
                                                  glucosa__gt=0).count()
                    if veces is 0:
                        veces = 1;
                    for instance in query_set:
                        calorias = calorias + instance.calorias;
                        glucosa = glucosa + instance.glucosa;

                    data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                            'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                    listal.append(data)
                    calorias = 0
                    data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                                    'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                    lista_glucosa.append(data_glucosa)
                    glucosa_global = glucosa_global + glucosa;
                    glucosa = 0

                if glucosa_global > 0:
                    diabetes = True;

                dias_inicio = dias_inicio.isoformat()
                row_json = mark_safe(json.dumps(listal))
                row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

                return render(request, "charts.html",
                              {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final,
                               'diabetes': diabetes,
                               'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                               })

    else:

        fecha = date.today()
        semana = fecha.isocalendar()[1]
        ########################################### calculo de los días de la semana correspondiente
        auxiliar = fecha.weekday()
        form = Semana(initial={'idSemana': semana})
        user = request.user



        if auxiliar == 0:

            dias_inicio = fecha
            dias_final = fecha + timedelta(days=6)
            dias_final = dias_final.isoformat()

            for i in range(0, 7):
                fecha_aux = (dias_inicio + timedelta(days=i))
                queryweek.append(fecha_aux.day)
                query_set = Comida.objects.filter(fecha_comida=fecha_aux,
                                                  paciente__user__username=username.get_username())
                veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                              paciente__user__username=username.get_username(),
                                              glucosa__gt=0).count()

                if veces is 0:
                    veces = 1;
                for instance in query_set:
                    calorias = calorias + instance.calorias;
                    glucosa = glucosa + instance.glucosa;

                data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                        'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                listal.append(data)
                calorias = 0
                data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                                'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                lista_glucosa.append(data_glucosa)
                glucosa_global = glucosa_global + glucosa;
                glucosa = 0

            if glucosa_global > 0:
                diabetes = True;

            dias_inicio = dias_inicio.isoformat()
            row_json = mark_safe(json.dumps(listal))
            row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

            return render(request, "charts.html",
                          {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final, 'diabetes': diabetes,
                           'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                           })


        else:

            dias_inicio = fecha - timedelta(days=fecha.weekday())
            dias_final = dias_inicio + timedelta(days=6)
            dias_final = dias_final.isoformat()

            for i in range(0, 7):
                fecha_aux = (dias_inicio + timedelta(days=i))
                query_set=Comida.objects.filter(fecha_comida=fecha_aux,paciente__user__username=username.get_username())
                veces = Comida.objects.filter(fecha_comida=fecha_aux,
                                              paciente__user__username=username.get_username(),
                                              glucosa__gt=0).count()
                if veces is 0:
                    veces = 1;

                for instance in query_set:
                    calorias = calorias + instance.calorias;
                    glucosa = glucosa + instance.glucosa;

                data = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                        'freq': {'low': float(calorias), 'mid': 0, 'high': 0}}
                listal.append(data)
                calorias = 0
                data_glucosa = {'State': semana_literal[i] + ' ' + str(fecha_aux.day),
                                'freq': {'low': float(glucosa/veces), 'mid': 0, 'high': 0}}
                lista_glucosa.append(data_glucosa)
                glucosa_global = glucosa_global + glucosa;
                glucosa = 0

            if glucosa_global > 0:
                diabetes = True;

            dias_inicio = dias_inicio.isoformat()
            row_json = mark_safe(json.dumps(listal))
            row_json_glucosa = mark_safe(json.dumps(lista_glucosa))

            return render(request, "charts.html",
                          {'semana': semana, 'dias_inicio': dias_inicio, 'dias_final': dias_final, 'diabetes': diabetes,
                           'form': form, 'chart': row_json, 'glucosa': row_json_glucosa, 'user': username
                           })
