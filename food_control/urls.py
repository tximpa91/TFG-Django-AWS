"""food_control URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.contrib.auth.views import login,logout,password_reset,password_reset_done,password_reset_complete
import alimentus.views
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls,name='admin'),
    url(r'^$', alimentus.views.login,name='login'),
    url(r'^login/$', alimentus.views.login,name='login'),
    url(r'^logout$', alimentus.views.log_out,name='logout'),
    url(r'^home/$', alimentus.views.home, name='home'),
    url(r'^signup/$', alimentus.views.signup,name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/',alimentus.views.activate,name='activate'),
    url(r'^reset_confirm/(?P<uidb64>[0-9A-Za-z]+)/(?P<uidb65>[0-9A-Za-z]+)$', alimentus.views.reset_confirm, name='reset_confirm'),
    url(r'^password_reset_form/$', alimentus.views.reset, name='reset'),
    url(r'^change_password/$',alimentus.views.change_password,name='change_password'),
    url(r'^ajax/validate_username/$',alimentus.views.validate_username,name='validate_username'),
    url(r'^oauth2/', include('social_django.urls', namespace='social')),
    url(r'^complete_profile/$', alimentus.views.complete_profile, name='complete_profile'),
    url(r'^pacient/$', alimentus.views.complete_profile, name='pacient'),
    url(r'^appointment/(?P<username>.+)$', alimentus.views.citas, name='citas'),
    url(r'^signup_pacient/$', alimentus.views.signup_doctor, name='paciente_doctor'),
    url(r'^add_food/$', alimentus.views.crear_alimento, name='alimento'),
    url(r'^personal_info/$', alimentus.views.personal_info, name='informacion'),
    url(r'^ajax/delete/$', alimentus.views.eliminar_citas, name='eliminar_citas'),
    url(r'^query_pacient/$', alimentus.views.busca_pacientes, name='busca_pacientes'),
    url(r'^food_type/$', alimentus.views.tipo_comida, name='tipo_comida'),
    url(r'^food_register/(?P<tipo>.+)$', alimentus.views.registrar_comida, name='registrar_comida'),
    url(r'^load_food/$', alimentus.views.query_alimentos, name='buscar_alimento'),
    url(r'^food_chart/(?P<username>.+)$', alimentus.views.progress_charts, name='progreso_nutricional')




]
