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


class BarberosAdmin(admin.ModelAdmin):
    form = UserBarberoForm
    list_display = ('nombre', 'apellido_paterno', 'apellido_materno', 'telefono', 'user')

    def save_model(self, request, obj, form, change):
        # Verificar si el barbero ya tiene un usuario relacionado
        if not obj.pk:  # Si es un barbero nuevo
            user = User()
        else:  # Si ya existe, obtenemos el usuario relacionado
            user = obj.user

        # Actualizamos los datos del usuario desde el formulario
        user.username = form.cleaned_data['username']
        user.email = form.cleaned_data['email']

        # Si se proporciona una nueva contraseña, actualizarla
        password = form.cleaned_data.get('password')
        if password:
            user.set_password(password)

        # Guardar el usuario antes de asignarlo al barbero
        user.save()

        # Asignar el usuario al barbero y luego guardar el barbero
        obj.user = user
        super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(Cliente)
#admin.site.register(Barberos)  
admin.site.register(Servicios)
#admin.site.register(EstadoCitas)
admin.site.register(Barberos,BarberosAdmin)
#admin.site.register(Citas)

# Desregistrar los modelos
# Verifica si PeriodicTask y CrontabSchedule están registrados antes de desregistrarlos

admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
# Para remover estas líneas si existen:
admin.site.unregister(blacklist_admin.BlacklistedToken)
admin.site.unregister(blacklist_admin.OutstandingToken)