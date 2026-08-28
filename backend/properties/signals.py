from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import PropertyImage


@receiver(pre_save, sender=PropertyImage)
def remember_replaced_image(sender, instance, **kwargs):
    instance._replaced_image = None
    if not instance.pk:
        return
    try:
        previous = sender.objects.only("image").get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    if previous.image.name and previous.image.name != instance.image.name:
        instance._replaced_image = previous.image


@receiver(post_save, sender=PropertyImage)
def delete_replaced_image(sender, instance, **kwargs):
    replaced_image = getattr(instance, "_replaced_image", None)
    if replaced_image:
        transaction.on_commit(lambda: replaced_image.delete(save=False))


@receiver(post_delete, sender=PropertyImage)
def delete_removed_image(sender, instance, **kwargs):
    if instance.image:
        image = instance.image
        transaction.on_commit(lambda: image.delete(save=False))
