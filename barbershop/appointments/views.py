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
import pytz
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
# Create your views here.

class ServiciosViewSet(viewsets.ModelViewSet):
    queryset = Servicios.objects.all()
    serializer_class = ServiciosSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

class BarberosViewSet(viewsets.ModelViewSet):
    queryset = Barberos.objects.all()
    serializer_class = BarberosSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

class CitasViewSet(viewsets.ModelViewSet):
    queryset = Citas.objects.all()
    serializer_class = CitasSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

class EstadoCitasViewSet(viewsets.ModelViewSet):
    queryset = EstadoCitas.objects.all()
    serializer_class = EstadoCitasSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

class CitasByBarber(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        barber_id = request.user.barberos.id_barbero
        citas = Citas.objects.filter(id_barbero=barber_id)
        if not citas.exists():
            return Response({"message": "No se encontraron citas para este barbero"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CitasSerializer(citas, many=True)
        return Response(serializer.data)
    
class CitasByBarberSchedule(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        barber_id = request.user.barberos.id_barbero
        citas = Citas.objects.filter(id_barbero=barber_id, id_estado__in=[1,7,4,6])
        if not citas.exists():
            return Response({"message": "No se encontraron citas para este barbero"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CitasSerializer(citas, many=True)
        return Response(serializer.data)

class AvailableSlotsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        barber_id = request.user.barberos
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
        local_tz = pytz.timezone('America/Mexico_City')  # Ajusta esto a tu zona horaria local
        work_start_time = local_tz.localize(datetime.combine(date, datetime.strptime('08:00', '%H:%M').time()))
        work_end_time = local_tz.localize(datetime.combine(date, datetime.strptime('21:00', '%H:%M').time()))

        # Obtener la hora actual en la zona horaria local
        now = timezone.now().astimezone(local_tz).date()


        if date < now:
            return Response({'error': 'La fecha no puede ser menor a la fecha actual'}, status=status.HTTP_400_BAD_REQUEST)

        # Si la fecha es hoy, ajustar el horario de inicio para que sea una hora después de la hora actual
        if date == now:
            next_hour = timezone.now().astimezone(local_tz) + timedelta(hours=1)
            #print(now)
            # Redondear al siguiente intervalo de 10 minutos
            next_hour = next_hour.replace(minute=(next_hour.minute // 10 + 1) * 10 % 60, second=0, microsecond=0)
            #print(now)
            work_start_time = max(work_start_time, next_hour)

        print(work_start_time)

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
            if appointment.id_estado.id_estado != 1:
                continue
            print(appointment)
            appointment_start = appointment.fecha_inicio
            appointment_end = appointment.fecha_finalizacion
            # Remover intervalos que estén dentro de los tiempos de las citas
            print(f"Inciio: {appointment_start} - Fin: {appointment_end}")
            filtered_slots = []
            for slot in available_slots:
                # Comprobar si el slot está completamente fuera del rango de la cita
                print(slot)
                print(appointment_start)
                if slot >= appointment_start and slot < appointment_end:
                    continue
                slot_end = slot + service_duration

                if slot_end > appointment_start and slot_end <= appointment_end:
                    continue
                filtered_slots.append(slot)
                

            # Actualizar la lista de slots disponibles
            available_slots = filtered_slots

        # Convertir las horas a formato legible (por ejemplo: 08:00, 08:10, etc.)
        available_slots_formatted = [slot.time().strftime('%H:%M') for slot in available_slots]
        print(f"Available slots: {available_slots_formatted}")

        return Response({'available_slots': available_slots_formatted}, status=status.HTTP_200_OK)
    
class CreateAppointmentView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        barber_id = request.user.barberos
        client_id = request.data.get('id_cliente')
        service_id = request.data.get('id_servicio')
        start_datetime_str = request.data.get('fecha_inicio')

        if not barber_id or not client_id or not service_id or not start_datetime_str:
            return Response({'error': 'Faltan parametros'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
        except ValueError:
            return Response({'error': 'Formato de fecha y hora invalido'}, status=status.HTTP_400_BAD_REQUEST)

        # Convertir la fecha y hora de inicio a la zona horaria local
        try:
            start_datetime = timezone.make_aware(start_datetime, timezone.get_current_timezone())
        except Exception as e:
            return Response({'error': 'Error al convertir la zona horaria'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
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
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
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
    
class CompleteAppointmentView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def patch(self, request, appointment_id):
        try:
            appointment = Citas.objects.get(id_cita=appointment_id)
        except Citas.DoesNotExist:
            return Response({'error': 'Cita no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        try:
            estado_reprogramado = EstadoCitas.objects.get(id_estado=6)
        except EstadoCitas.DoesNotExist:
            return Response({'error': 'Estado completada no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        appointment.id_estado = estado_reprogramado
        appointment.save()

        return Response({'message': 'Estado de la cita actualizado a completada'}, status=status.HTTP_200_OK)