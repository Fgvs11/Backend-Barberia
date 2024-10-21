from django.shortcuts import render
from rest_framework import viewsets
from .models import Servicios, Cliente, Barberos, Citas, EstadoCitas
from .serializers import ServiciosSerializer, ClienteSerializer, BarberosSerializer, CitasSerializer, EstadoCitasSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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

class CitasByBarber(APIView):
    def get(self, request, barber_id):
        citas = Citas.objects.filter(id_barbero=barber_id)
        if not citas.exists():
            return Response({"message": "No se encontraron citas para este barbero"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CitasSerializer(citas, many=True)
        return Response(serializer.data)
        