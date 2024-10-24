from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establecer el módulo de configuración predeterminado de Django para 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbershop.settings')

app = Celery('barbershop')

# Usar una cadena aquí significa que el worker no tendrá que serializar
# la configuración del objeto en cada tarea.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar tareas de todos los módulos de aplicaciones registradas en Django.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')