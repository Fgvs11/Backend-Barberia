# Generated by Django 5.1.1 on 2024-10-24 19:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0002_alter_barberos_telefono_alter_cliente_telefono'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='barberos',
            name='user',
            field=models.OneToOneField(default=3, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='citas',
            name='id_estado',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='appointments.estadocitas'),
        ),
    ]
