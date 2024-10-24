from django.contrib import admin
from .models import Cliente, Barberos, Servicios, EstadoCitas, Citas
from .forms import UserBarberoForm

class BarberosAdmin(admin.ModelAdmin):
    form = UserBarberoForm
    list_display = ('nombre', 'apellido_paterno', 'apellido_materno', 'telefono', 'user')  # Mostrar el usuario relacionado

    # Mostrar los campos de usuario en la vista del admin
    def get_form(self, request, obj=None, **kwargs):
        form = super(BarberosAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['username'].label = "Nombre de Usuario"
        form.base_fields['email'].label = "Correo Electrónico"
        form.base_fields['password'].label = "Contraseña"
        return form


# Register your models here.
admin.site.register(Cliente)
#admin.site.register(Barberos)  
admin.site.register(Servicios)
admin.site.register(EstadoCitas)
admin.site.register(Barberos,BarberosAdmin)
#admin.site.register(Citas)
