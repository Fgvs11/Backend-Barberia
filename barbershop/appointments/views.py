from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from .models import Servicios, Cliente, Barberos, Citas, EstadoCitas
from .serializers import ServiciosSerializer, ClienteSerializer, BarberosSerializer, CitasSerializer, EstadoCitasSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth, TruncDay
import pytz
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.views.generic import DetailView, TemplateView
from .utils import send_sms
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import json
from django.views.generic import View
from django.utils.timezone import now
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
        barber_id = request.user.barberos.id_barbero
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
        barber_id = request.user.barberos.id_barbero
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
        client_phone = "+52" + client.telefono
        url = f"https://kings-man-barber-shop-api.software/api/cita/{appointment.tokenName}/ "
        sms_body = f"Hola {client.nombre} {client.apellido_paterno} {client.apellido_materno}, Entendemos que tus planes pueden cambiar. Para cancelar tu cita fácilmente, solo sigue este enlace:\n {url}\nSi deseas reprogramar o necesitas ayuda, no dudes en contactarnos. Esperamos verte pronto."
        try:
            send_sms(client_phone, sms_body)
        except Exception as e:
            print(e)
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
        appointment.token = False
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
        appointment.token = False
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
        appointment.token = False
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
        appointment.token = False
        appointment.save()

        return Response({'message': 'Estado de la cita actualizado a completada'}, status=status.HTTP_200_OK)
    
class AppointmentDetailView(DetailView):
    model = Citas
    template_name = 'appointments/detalle_cita.html'
    context_object_name = 'cita'

    def get_object(self, queryset=None):
        # Obtener el objeto cita y verificar si el token está en True
        tokenName = self.kwargs.get('tokenName')
        cita = get_object_or_404(Citas, tokenName=tokenName)
        if not cita.token or cita.id_estado.id_estado != 1:
            # Si el token está en False, denegar el acceso
            self.template_name = 'appointments/acceso_denegado.html'
        return cita

    def post(self, request, *args, **kwargs):
        # Obtener la cita usando get_object (que ya verifica el token)
        cita = self.get_object()
        
        # Verificar si el usuario quiere cancelar la cita
        if 'cancel' in request.POST:
            tiempo_restante = cita.fecha_inicio - timezone.now()
            horas_restantes = tiempo_restante.total_seconds() / 3600
            if horas_restantes < 2:
                # Cambia el estado de la cita a 'falta' y guarda
                estado_falta = get_object_or_404(EstadoCitas, id_estado=4)
                cita.id_estado = estado_falta
                cita.token = False
                cita.save()
                return render(request, 'appointments/cita_falta.html')
            # Cambia el estado de la cita a 'cancelado' y guarda
            estado_cancelado = get_object_or_404(EstadoCitas, id_estado=2)
            cita.id_estado = estado_cancelado
            cita.token = False
            cita.save()
            # Redirige a una página de confirmación o muestra el mensaje
            client = cita.id_cliente
            client_phone = "+52" + client.telefono
            try:
                send_sms(client_phone, f"Tu cita ha sido cancelada. Para más información, contacta a tu barbero.")
            except Exception as e:
                print(e)
            return render(request, 'appointments/cita_cancelada.html', {'cita': cita})

        # Si no se presiona cancelar, renderizar la página de detalles
        return self.get(request, *args, **kwargs)

class DashboardView(TemplateView):
    template_name = 'appointments/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el mes seleccionado de los parámetros de la URL
        selected_month = self.request.GET.get('month')
        if selected_month:
            try:
                selected_month_date = datetime.strptime(selected_month, '%Y-%m')
                citas = Citas.objects.filter(fecha_inicio__year=selected_month_date.year, fecha_inicio__month=selected_month_date.month)
                citas_por_dia = citas.annotate(day=TruncDay('fecha_inicio')).values('day').annotate(count=Count('id_cita')).order_by('day')
            except ValueError:
                citas = Citas.objects.all()
                citas_por_dia = []
        else:
            citas = Citas.objects.all()
            citas_por_dia = []

        # Datos generales
        total_citas = citas.count()
        total_clientes = Cliente.objects.count()
        total_barberos = Barberos.objects.count()

        # Datos de las citas
        estados_citas = citas.values('id_estado__nombre').annotate(count=Count('id_estado'))
        servicios_citas = citas.values('id_servicio__nombre').annotate(count=Count('id_servicio'))
        barberos_citas = citas.values('id_barbero__nombre').annotate(count=Count('id_barbero'))
        clientes_citas = citas.values('id_cliente__nombre').annotate(count=Count('id_cliente'))

        # Gráfico circular de estados de citas
        fig_estados = {
            'data': [{'labels': [estado['id_estado__nombre'] for estado in estados_citas],
                      'values': [estado['count'] for estado in estados_citas],
                      'type': 'pie'}],
            'layout': {'title': 'Distribución de Citas por Estado'}
        }
        context['estado_pie_chart_json'] = json.dumps(fig_estados)

        # Gráfico circular de servicios de citas
        fig_servicios = {
            'data': [{'labels': [servicio['id_servicio__nombre'] for servicio in servicios_citas],
                      'values': [servicio['count'] for servicio in servicios_citas],
                      'type': 'pie'}],
            'layout': {'title': 'Distribución de Citas por Servicio'}
        }
        context['servicio_pie_chart_json'] = json.dumps(fig_servicios)

        # Gráfico circular de barberos de citas
        fig_barberos = {
            'data': [{'labels': [barbero['id_barbero__nombre'] for barbero in barberos_citas],
                      'values': [barbero['count'] for barbero in barberos_citas],
                      'type': 'pie'}],
            'layout': {'title': 'Distribución de Citas por Barbero'}
        }
        context['barbero_pie_chart_json'] = json.dumps(fig_barberos)

        # Gráfico circular de clientes
        fig_cliente = {
            'data': [{'labels': [cliente['id_cliente__nombre'] for cliente in clientes_citas],
                      'values': [cliente['count'] for cliente in clientes_citas],
                      'type': 'pie'}],
            'layout': {'title': 'Distribución de Citas por Cliente'}
        }
        context['cliente_pie_chart_json'] = json.dumps(fig_cliente)

        # Gráfico de línea de citas por día del mes o por mes
        if selected_month:
            fig_citas_mes = {
                'data': [{'x': [cita['day'].strftime('%Y-%m-%d') for cita in citas_por_dia],
                          'y': [cita['count'] for cita in citas_por_dia],
                          'type': 'scatter',
                          'mode': 'lines+markers'}],
                'layout': {'title': f'Citas por Día en {selected_month_date.strftime("%B %Y")}'}
            }
        else:
            citas_por_mes = Citas.objects.annotate(month=TruncMonth('fecha_inicio')).values('month').annotate(count=Count('id_cita')).order_by('month')
            fig_citas_mes = {
                'data': [{'x': [cita['month'].strftime('%Y-%m') for cita in citas_por_mes],
                          'y': [cita['count'] for cita in citas_por_mes],
                          'type': 'scatter',
                          'mode': 'lines+markers'}],
                'layout': {'title': 'Citas por Mes'}
            }
        context['citas_mes_chart_json'] = json.dumps(fig_citas_mes)

        # Datos generales
        context['total_citas'] = total_citas
        context['total_clientes'] = total_clientes
        context['total_barberos'] = total_barberos
        context['selected_month'] = selected_month

        return context