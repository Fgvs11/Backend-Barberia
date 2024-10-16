from django.shortcuts import render
from rest_framework import viewsets
from .models import Servicios, Cliente, Barberos, Citas, EstadoCitas
from .serializers import ServiciosSerializer, ClienteSerializer, BarberosSerializer, CitasSerializer, EstadoCitasSerializer
# Create your views here.

class ServiciosViewSet(viewsets.ModelViewSet):
    queryset = Servicios.objects.all()
    serializer_class = ServiciosSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class BarberosViewSet(viewsets.ModelViewSet):
    queryset = Barberos.objects.all()
    serializer_class = BarberosSerializer

class CitasViewSet(viewsets.ModelViewSet):
    queryset = Citas.objects.all()
    serializer_class = CitasSerializer

class EstadoCitasViewSet(viewsets.ModelViewSet):
    queryset = EstadoCitas.objects.all()
    serializer_class = EstadoCitasSerializer
