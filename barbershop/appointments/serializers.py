from rest_framework import serializers
from .models import Servicios, Cliente, Barberos, Citas, EstadoCitas

class ServiciosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicios
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class BarberosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barberos
        fields = '__all__'

class CitasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citas
        fields = '__all__'

class EstadoCitasSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCitas
        fields = '__all__'

