# Generated by Django 5.1.1 on 2024-10-24 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0003_barberos_user_alter_citas_id_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='barberos',
            name='nombre',
            field=models.CharField(max_length=50),
        ),
    ]
