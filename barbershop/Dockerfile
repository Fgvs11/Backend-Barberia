FROM python:3.12.5-slim
ENV PYTHONUNBUFFERED 1
WORKDIR /barbershop
RUN pip install --upgrade pip
COPY requirements.txt /barbershop/
RUN pip install -r requirements.txt
COPY . /barbershop/
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]