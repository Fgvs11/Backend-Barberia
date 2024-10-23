# Backend-Barberia
# Acomodar la base de datos
En la consola de postgres colocar los comandos de el archivo db.txt
# Instalar los paquetes necesarios de python
Estos se encuentran en requirements.txt y para instalarlos ejecutar el siguiente comando desde la carpeta de barbershop
`RUN pip install -r requirements.txt`
# Por ultimo hacer las respectivas migraciones a la base de datos:
Para ello ejecutar los siguientes comandos
`python manage.py makemigrations`
`python manage.py migrate`

# Listo solo queda ejecutar el server
`python manage.py runserver`
`celery -A barbershop worker --loglevel=info`
`celery -A barbershop beat --loglevel=info`

# To do list

- Use docker for production
- Make the authentification work
- Make the users table with the barber_id relationship
