@echo off
echo Iniciando el servidor de Django...
start cmd /k "python manage.py runserver"

echo Iniciando el worker de Celery...
start cmd /k "celery -A barbershop worker --loglevel=info"

echo Iniciando el scheduler de Celery...
start cmd /k "celery -A barbershop beat --loglevel=info"

echo Todos los servicios han sido iniciados.
