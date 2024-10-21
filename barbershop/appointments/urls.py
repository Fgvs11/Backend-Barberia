from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiciosViewSet, ClienteViewSet, BarberosViewSet, CitasViewSet, EstadoCitasViewSet, CitasByBarber, AvailableSlotsView, CreateAppointmentView,RescheduleAppointmentView, CancelBAppointmentView, CancelCAppointmentView, MissAppointmentView
from .views import CitasByBarberSchedule
router = DefaultRouter()
router.register(r'servicios', ServiciosViewSet)  # /api/servicios
router.register(r'cliente', ClienteViewSet)  # /api/cliente
router.register(r'barberos', BarberosViewSet)  # /api/barberos
router.register(r'citas', CitasViewSet)  # /api/citas
router.register(r'estado-citas', EstadoCitasViewSet)  # /api/estado-citas


urlpatterns = [
    path('', include(router.urls)),
    path('citas/barbero/<int:barber_id>/', CitasByBarber.as_view(), name='citas-by-barber'), #api/citas/barbero/<int:barber_id>/
    path('citas/barbero/<int:barber_id>/filter', CitasByBarberSchedule.as_view(), name='citas-by-barber'), #api/citas/barbero/<int:barber_id>/filter
    path('horarios-disponibles/', AvailableSlotsView.as_view(), name='horarios-disponibles'), #api/horarios-disponibles/
    path('citas/crear', CreateAppointmentView.as_view(), name='crear-cita'), #api/citas/crear
    path('citas/reprogramar/<int:appointment_id>/', RescheduleAppointmentView.as_view(), name='reprogramar-cita'), #api/citas/reprogramar/<int:appointment_id>/
    path('citas/cancelar/barbero/<int:appointment_id>/', CancelBAppointmentView.as_view(), name='cancelar-cita-barbero'), #api/citas/cancelar/barbero<int:appointment_id>/
    path('citas/cancelar/cliente/<int:appointment_id>/', CancelCAppointmentView.as_view(), name='cancelar-cita-cliente'), #api/citas/cancelar/cliente/<int:appointment_id>/
    path('citas/falto/<int:appointment_id>/', MissAppointmentView.as_view(), name='falto-cita'), #api/citas/falto/<int:appointment_id>/
]
