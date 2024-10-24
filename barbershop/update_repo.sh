#!/bin/bash

# Navega al directorio del proyecto
cd /var/www/Backend-Barberia/barbershop

# Activa el entorno virtual
source venv/bin/activate

# Trae los cambios más nuevos del repositorio
git pull origin main

# Instala nuevas dependencias
pip install -r requirements.txt

# Aplica migraciones de la base de datos
python manage.py migrate

# Recopila archivos estáticos
python manage.py collectstatic --noinput

# Reinicia Gunicorn para aplicar los cambios
sudo systemctl restart gunicorn