from celery import shared_task
from django.utils import timezone
from .models import Citas, EstadoCitas

@shared_task
def update_appointment_status():
    now = timezone.now()
    pending_status = EstadoCitas.objects.get(id_estado=7)
    citas = Citas.objects.filter(fecha_inicio__lte=now, id_estado=1)
    citas.update(id_estado=pending_status.id_estado)