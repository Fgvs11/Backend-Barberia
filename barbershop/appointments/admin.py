from django.contrib import admin
from .models import Cliente, Barberos, Servicios, EstadoCitas, Citas
from django.contrib.auth.models import User
from .forms import UserBarberoForm
from rest_framework_simplejwt.token_blacklist import admin as blacklist_admin
from django_celery_beat.models import (
    IntervalSchedule,
    CrontabSchedule,
    SolarSchedule,
    ClockedSchedule,
    PeriodicTask,
)
from django.apps import apps
from django.urls import reverse
from django.utils.html import format_html


class BarberosAdmin(admin.ModelAdmin):
    form = UserBarberoForm
    list_display = ('nombre', 'apellido_paterno', 'apellido_materno', 'telefono', 'user')
    search_fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'telefono', 'user__username']




# Register your models here.
admin.site.register(Cliente)
#admin.site.register(Barberos)  
admin.site.register(Servicios)
#admin.site.register(EstadoCitas)
admin.site.register(Barberos,BarberosAdmin)
#admin.site.register(Citas)

# Desregistrar los modelos
# Verifica si PeriodicTask y CrontabSchedule están registrados antes de desregistrarlos

if apps.is_installed('django_celery_beat'):
    try:
        admin.site.unregister(PeriodicTask)
    except admin.sites.NotRegistered:
        pass
    try:
        admin.site.unregister(CrontabSchedule)
    except admin.sites.NotRegistered:
        pass
    try:
        admin.site.unregister(IntervalSchedule)
    except admin.sites.NotRegistered:
        pass
    try:
        admin.site.unregister(SolarSchedule)
    except admin.sites.NotRegistered:
        pass
    try:
        admin.site.unregister(ClockedSchedule)
    except admin.sites.NotRegistered:
        pass

# Para remover estas líneas si existen:
admin.site.unregister(blacklist_admin.BlacklistedToken)
admin.site.unregister(blacklist_admin.OutstandingToken)