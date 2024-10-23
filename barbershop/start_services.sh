#!/bin/bash

# Iniciar el servidor de Django
echo "Iniciando el servidor de Django..."
gnome-terminal -- bash -c "python manage.py runserver; exec bash"

# Iniciar el worker de Celery
echo "Iniciando el worker de Celery..."
gnome-terminal -- bash -c "celery -A barbershop worker --loglevel=info; exec bash"

# Iniciar el scheduler de Celery
echo "Iniciando el scheduler de Celery..."
gnome-terminal -- bash -c "celery -A barbershop beat --loglevel=info; exec bash"

echo "Todos los servicios han sido iniciados."