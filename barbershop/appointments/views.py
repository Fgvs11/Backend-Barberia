from django.shortcuts import render
from rest_framework import viewsets
from .models import Servicios, Cliente, Barberos, Citas, EstadoCitas
from .serializers import ServiciosSerializer, ClienteSerializer, BarberosSerializer, CitasSerializer, EstadoCitasSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone

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

class AvailableSlotsView(APIView):
    def post(self, request):
        barber_id = request.data.get('barber_id')
        service_id = request.data.get('service_id')
        date = request.data.get('date')

        if not barber_id or not service_id or not date:
            return Response({'error': 'Faltan parametros'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Formato de fecha invalida'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener la duración del servicio
        try:
            service = Servicios.objects.get(id_servicio=service_id)
            service_duration = timedelta(minutes=int(service.tiempo_aproximado * 60))
        except Servicios.DoesNotExist:
            return Response({'error': 'Service no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Definir el horario de trabajo (ejemplo: 9:00 AM a 5:00 PM)
        work_start_time = timezone.make_aware(datetime.combine(date, datetime.strptime('08:00', '%H:%M').time()))  # Hacer timezone-aware
        work_end_time = timezone.make_aware(datetime.combine(date, datetime.strptime('21:00', '%H:%M').time()))    # Hacer timezone-aware

        # Obtener todas las citas del barbero para el día especificado
        appointments = Citas.objects.filter(id_barbero=barber_id, fecha_inicio__date=date)

        # Generar todos los intervalos de 10 minutos dentro del horario de trabajo
        available_slots = []
        current_time = work_start_time
        while current_time + service_duration <= work_end_time:
            available_slots.append(current_time)
            current_time += timedelta(minutes=10)
        
        # Filtrar los intervalos que están ocupados por citas
        for appointment in appointments:
            appointment_start = appointment.fecha_inicio
            appointment_end = appointment.fecha_finalizacion
            
            if timezone.is_naive(appointment_start):
                appointment_start = timezone.make_aware(appointment_start)
            if timezone.is_naive(appointment_end):
                appointment_end = timezone.make_aware(appointment_end)
            # Remover intervalos que estén dentro de los tiempos de las citas
            available_slots = [
                slot for slot in available_slots
                if not (appointment_start <= slot < appointment_end)
            ]

        # Convertir las horas a formato legible (por ejemplo: 08:00, 08:10, etc.)
        available_slots_formatted = [slot.time().strftime('%H:%M') for slot in available_slots]

        return Response({'available_slots': available_slots_formatted}, status=status.HTTP_200_OK)