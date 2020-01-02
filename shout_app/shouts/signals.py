from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Shout, Discussion, Comment

@receiver(post_save, sender=Shout)
def create_discussion(sender, instance, created, *args, **kwargs):
    if instance and created:
        Discussion.objects.create(shout=instance)

@receiver(post_save, sender=Comment)
def add_to_discussion(sender, instance, created, *args, **kwargs):
    if instance and created:
        discussion = Discussion.objects.get(shout=instance.commented_on)
        discussion.comments.add(instance)


