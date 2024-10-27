from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Barberos

@receiver(post_delete, sender=Barberos)
def delete_user_on_barbero_delete(sender, instance, **kwargs):
    # Si el barbero tiene un usuario asociado, elimínalo
    if instance.user:
        instance.user.delete()
