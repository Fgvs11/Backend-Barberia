from django.contrib import admin
from .models import Cliente, Barberos, Servicios, EstadoCitas, Citas
# Register your models here.
admin.site.register(Cliente)
admin.site.register(Barberos)  
admin.site.register(Servicios)
admin.site.register(EstadoCitas)
admin.site.register(Citas)
