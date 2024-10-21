from django.shortcuts import render
from rest_framework import viewsets
from .models import Servicios, Cliente, Barberos, Citas, EstadoCitas
from .serializers import ServiciosSerializer, ClienteSerializer, BarberosSerializer, CitasSerializer, EstadoCitasSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
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
    
class CitasByBarberSchedule(APIView):
    def get(self, request, barber_id):
        citas = Citas.objects.filter(id_barbero=barber_id).filter(Q(id_estado=1) | Q(id_estado=6))
        if not citas.exists():
            return Response({"message": "No se encontraron citas para este barbero"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CitasSerializer(citas, many=True)
        return Response(serializer.data)

class AvailableSlotsView(APIView):
    def post(self, request):
        barber_id = request.data.get('id_barbero')
        service_id = request.data.get('id_servicio')
        date = request.data.get('fecha')

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
            if appointment.id_estado != 1:
                continue
            
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


class CreateAppointmentView(APIView):
    def post(self, request):
        barber_id = request.data.get('id_barbero')
        client_id = request.data.get('id_cliente')
        service_id = request.data.get('id_servicio')
        start_datetime_str = request.data.get('fecha_inicio')

        if not barber_id or not client_id or not service_id or not start_datetime_str:
            return Response({'error': 'Faltan parametros'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
        except ValueError:
            return Response({'error': 'Formato de fecha y hora invalido'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener la duración del servicio
        try:
            service = Servicios.objects.get(id_servicio=service_id)
            service_duration = timedelta(minutes=int(service.tiempo_aproximado * 60))
        except Servicios.DoesNotExist:
            return Response({'error': 'Servicio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Calcular la fecha de finalización
        end_datetime = start_datetime + service_duration

        # Crear la cita
        try:
            barber = Barberos.objects.get(id_barbero=barber_id)
            client = Cliente.objects.get(id_cliente=client_id)
            appointment = Citas.objects.create(
                id_barbero=barber,
                id_cliente=client,
                id_servicio=service,
                fecha_inicio=start_datetime,
                fecha_finalizacion=end_datetime
            )
        except Barberos.DoesNotExist:
            return Response({'error': 'Barbero no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Cliente.DoesNotExist:
            return Response({'error': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'Cita creada exitosamente', 'appointment_id': appointment.id_cita}, status=status.HTTP_201_CREATED)
    
class RescheduleAppointmentView(APIView):
    def patch(self, request, appointment_id):
        try:
            appointment = Citas.objects.get(id_cita=appointment_id)
        except Citas.DoesNotExist:
            return Response({'error': 'Cita no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        try:
            estado_reprogramado = EstadoCitas.objects.get(id_estado=3)
        except EstadoCitas.DoesNotExist:
            return Response({'error': 'Estado reprogramado no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        appointment.id_estado = estado_reprogramado
        appointment.save()

        return Response({'message': 'Estado de la cita actualizado a reprogramada'}, status=status.HTTP_200_OK)
    
class CancelBAppointmentView(APIView):
    def patch(self, request, appointment_id):
        try:
            appointment = Citas.objects.get(id_cita=appointment_id)
        except Citas.DoesNotExist:
            return Response({'error': 'Cita no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        try:
            estado_reprogramado = EstadoCitas.objects.get(id_estado=5)
        except EstadoCitas.DoesNotExist:
            return Response({'error': 'Estado cancelado por el barbero no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        appointment.id_estado = estado_reprogramado
        appointment.save()

        return Response({'message': 'Estado de la cita actualizado a cancelada por el barbero'}, status=status.HTTP_200_OK)
    
class CancelCAppointmentView(APIView):
    def patch(self, request, appointment_id):
        try:
            appointment = Citas.objects.get(id_cita=appointment_id)
        except Citas.DoesNotExist:
            return Response({'error': 'Cita no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        try:
            estado_reprogramado = EstadoCitas.objects.get(id_estado=2)
        except EstadoCitas.DoesNotExist:
            return Response({'error': 'Estado cancelado por el cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        appointment.id_estado = estado_reprogramado
        appointment.save()

        return Response({'message': 'Estado de la cita actualizado a cancelada por el cliente'}, status=status.HTTP_200_OK)
    
class MissAppointmentView(APIView):
    def patch(self, request, appointment_id):
        try:
            appointment = Citas.objects.get(id_cita=appointment_id)
        except Citas.DoesNotExist:
            return Response({'error': 'Cita no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        try:
            estado_reprogramado = EstadoCitas.objects.get(id_estado=4)
        except EstadoCitas.DoesNotExist:
            return Response({'error': 'Estado no asistido no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        appointment.id_estado = estado_reprogramado
        appointment.save()

        return Response({'message': 'Estado de la cita actualizado a no asistido'}, status=status.HTTP_200_OK)