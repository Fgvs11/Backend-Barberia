from django.urls import path, include
"""
URL Configuration for the appointments app.
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Routes:
    - /api/servicios/:
        - ViewSet: ServiciosViewSet
        - Description: Endpoint for managing services.
        - Methods: GET, POST, PUT, DELETE
    - /api/cliente/:
        - ViewSet: ClienteViewSet
        - Description: Endpoint for managing clients.
        - Methods: GET, POST, PUT, DELETE
    - /api/barberos/:
        - ViewSet: BarberosViewSet
        - Description: Endpoint for managing barbers.
        - Methods: GET, POST, PUT, DELETE
    - /api/citas/:
        - ViewSet: CitasViewSet
        - Description: Endpoint for managing appointments.
        - Methods: GET, POST, PUT, DELETE
    - /api/estado-citas/:
        - ViewSet: EstadoCitasViewSet
        - Description: Endpoint for managing appointment statuses.
        - Methods: GET, POST, PUT, DELETE
    - /api/citas/barbero/<int:barber_id>/:
        - View: CitasByBarber
        - Description: Retrieve appointments by barber ID.
        - Methods: GET
    - /api/citas/barbero/<int:barber_id>/filter:
        - View: CitasByBarberSchedule
        - Description: Retrieve filtered appointments by barber ID.
        - Methods: GET
    - /api/horarios-disponibles/:
        - View: AvailableSlotsView
        - Description: Retrieve available time slots.
        - Methods: POST
        - Body: {
                    "id_barbero": 1,
                    "id_servicio": 1,
                    "fecha": "2024-10-21"
                }
    - /api/citas/crear:
        - View: CreateAppointmentView
        - Description: Create a new appointment.
        - Methods: POST
        - Body: {
                    "id_barbero": 1,
                    "id_cliente": 4,
                    "id_servicio": 1,
                    "fecha_inicio": "2024-10-26 10:00"
                }
    - /api/citas/reprogramar/<int:appointment_id>/:
        - View: RescheduleAppointmentView
        - Description: Reschedule an existing appointment by appointment ID.
        - Methods: PATCH
    - /api/citas/cancelar/barbero/<int:appointment_id>/:
        - View: CancelBAppointmentView
        - Description: Cancel an appointment by barber.
        - Methods: PATCH
    - /api/citas/cancelar/cliente/<int:appointment_id>/:
        - View: CancelCAppointmentView
        - Description: Cancel an appointment by client.
        - Methods: PATCH
    - /api/citas/falto/<int:appointment_id>/:
        - View: MissAppointmentView
        - Description: Mark an appointment as missed.
        - Methods: PATCH
"""
from rest_framework.routers import DefaultRouter
from .views import ServiciosViewSet, ClienteViewSet, BarberosViewSet, CitasViewSet, EstadoCitasViewSet, CitasByBarber, AvailableSlotsView, CreateAppointmentView,RescheduleAppointmentView, CancelBAppointmentView, CancelCAppointmentView, MissAppointmentView
from .views import CitasByBarberSchedule, CompleteAppointmentView
router = DefaultRouter()
router.register(r'servicios', ServiciosViewSet)  # /api/servicios
router.register(r'cliente', ClienteViewSet)  # /api/cliente
router.register(r'barberos', BarberosViewSet)  # /api/barberos
router.register(r'citas', CitasViewSet)  # /api/citas
router.register(r'estado-citas', EstadoCitasViewSet)  # /api/estado-citas


urlpatterns = [
    path('', include(router.urls)),
    path('citas/barbero/', CitasByBarber.as_view(), name='citas-by-barber'), #api/citas/barbero/  GET
    path('citas/barbero/filter/', CitasByBarberSchedule.as_view(), name='citas-by-barber'), #api/citas/filter/  GET
    path('horarios-disponibles/', AvailableSlotsView.as_view(), name='horarios-disponibles'), #api/horarios-disponibles/ POST
    path('citas/crear', CreateAppointmentView.as_view(), name='crear-cita'), #api/citas/crear POST
    path('citas/reprogramar/<int:appointment_id>/', RescheduleAppointmentView.as_view(), name='reprogramar-cita'), #api/citas/reprogramar/<int:appointment_id>/  PATCH
    path('citas/cancelar/barbero/<int:appointment_id>/', CancelBAppointmentView.as_view(), name='cancelar-cita-barbero'), #api/citas/cancelar/barbero<int:appointment_id>/ PATCH
    path('citas/cancelar/cliente/<int:appointment_id>/', CancelCAppointmentView.as_view(), name='cancelar-cita-cliente'), #api/citas/cancelar/cliente/<int:appointment_id>/ PATCH
    path('citas/falto/<int:appointment_id>/', MissAppointmentView.as_view(), name='falto-cita'), #api/citas/falto/<int:appointment_id>/ PATCH
    path('citas/completar/<int:appointment_id>/', CompleteAppointmentView.as_view(), name='completar-cita'), #api/citas/completar/<int:appointment_id>/ PATCH
]
