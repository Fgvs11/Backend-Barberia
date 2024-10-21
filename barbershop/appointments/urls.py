from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiciosViewSet, ClienteViewSet, BarberosViewSet, CitasViewSet, EstadoCitasViewSet, CitasByBarber, AvailableSlotsView

router = DefaultRouter()
router.register(r'servicios', ServiciosViewSet)  # /api/servicios
router.register(r'cliente', ClienteViewSet)  # /api/cliente
router.register(r'barberos', BarberosViewSet)  # /api/barberos
router.register(r'citas', CitasViewSet)  # /api/citas
router.register(r'estado-citas', EstadoCitasViewSet)  # /api/estado-citas


urlpatterns = [
    path('', include(router.urls)),
    path('citas/barbero/<int:barber_id>/', CitasByBarber.as_view(), name='citas-by-barber'), #api/citas/barbero/<int:barber_id>/
    path('available-slots/', AvailableSlotsView.as_view(), name='available_slots'), #api/available-slots/
]
