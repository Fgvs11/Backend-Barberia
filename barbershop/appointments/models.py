from datetime import timezone
from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.forms import ValidationError

# Create your models here.
class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key = True)
    nombre = models.CharField(max_length = 40)
    apellido_paterno = models.CharField(max_length = 30)
    apellido_materno = models.CharField(max_length = 30)
    telefono = models.CharField(max_length = 10,
                                validators = [MinLengthValidator(10),
                                              RegexValidator(r'^\d{10}$', 'El número de teléfono debe tener 10 dígitos')])
    fecha_registro = models.DateField(auto_now_add = True)

    def __str__(self):
        return self.nombre + ' ' + self.apellido_paterno + ' ' + self.apellido_materno
    
class Barberos(models.Model):
    id_barbero = models.AutoField(primary_key = True)
    nombre = models.CharField(max_length = 40)
    apellido_paterno = models.CharField(max_length = 30)
    apellido_materno = models.CharField(max_length = 30)
    telefono = models.CharField(max_length = 10,
                                validators = [MinLengthValidator(10),
                                              RegexValidator(r'^\d{10}$', 'El número de teléfono debe tener 10 dígitos')])

    def __str__(self):
        return self.nombre + ' ' + self.apellido_paterno + ' ' + self.apellido_materno
    
class Servicios(models.Model):
    id_servicio = models.AutoField(primary_key = True)
    nombre = models.CharField(max_length = 100)
    precio = models.DecimalField(max_digits = 5, decimal_places = 2)
    tiempo_aproximado = models.FloatField()

    def clean(self):
        if self.precio <= 0:
            raise ValidationError('El precio no puede ser negativo')
        if self.tiempo_aproximado <= 0:
            raise ValidationError('El tiempo aproximado no puede ser negativo')

    def __str__(self):
        return self.nombre
    
class EstadoCitas(models.Model):
    id_estado = models.AutoField(primary_key = True)
    nombre = models.CharField(max_length = 20)

    def __str__(self):
        return self.nombre
    
class Citas(models.Model):
    id_cita = models.AutoField(primary_key = True)
    id_cliente = models.ForeignKey(Cliente, on_delete = models.CASCADE)
    id_barbero = models.ForeignKey(Barberos, on_delete = models.CASCADE)
    id_servicio = models.ForeignKey(Servicios, on_delete = models.CASCADE)
    fecha_inicio= models.DateTimeField()
    fecha_finalizacion= models.DateTimeField()
    id_estado = models.ForeignKey(EstadoCitas,default=1, on_delete = models.CASCADE)
    token = models.BooleanField(default = True)

    def clean(self):
        if self.fecha_inicio >= self.fecha_finalizacion:
            raise ValidationError('La fecha de inicio no puede ser mayor o igual a la fecha de finalización')
        if self.fecha_inicio < timezone.now():
            raise ValidationError('La fecha de inicio no puede ser menor a la fecha actual')

    def __str__(self):
        return f"{self.cliente.nombre} {self.cliente.apellido_paterno} {self.cliente.apellido_materno} - {self.fecha_inicio} to {self.fecha_finalizacion}"