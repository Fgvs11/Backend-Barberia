from celery import shared_task
from django.utils import timezone
from .models import Citas, EstadoCitas

@shared_task
def update_appointment_status():
    now = timezone.now()
    pending_status = EstadoCitas.objects.get(id_estado=7)
    citas = Citas.objects.filter(fecha_inicio__lte=now, id_estado=1)
    print(f"Actualizando citas con fecha <= {now}. Número de citas: {citas.count()}")

    for cita in citas:
        print(f"Actualizando cita: {cita.id_cita} - Fecha inicio: {cita.fecha_inicio}")
        cita.id_estado = pending_status
        cita.save()