import json
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification
from .serializers import NotificationSerializer


@receiver(post_save)
def create_notification(sender, instance, created, **kwargs):
    if sender.__name__ == "OrganizationMemberShipRequest" and instance.status == 'A':
        Notification.objects.create(
            user=instance.client.user,
            title=_(f"Membership Request Accepted"),
            message=_(f"You have been accepted into {instance.organization.name}.")
        )
    elif sender.__name__ == "OrganizationMemberShipRequest" and instance.status == 'R':
        Notification.objects.create(
            user=instance.client.user,
            title=_(f"Membership Request Rejected"),
            message=_(f"Your request to join {instance.organization.name} has been rejected.")
        )
    elif sender.__name__ == "Transaction" and created:
        amount = instance.amount
        title = _(f"deposit {amount}") if amount > 0 else _(f"withdraw {-amount}")
        message = instance.description if instance.description else _(f"Transaction of {amount}")
        Notification.objects.create(
            user=instance.wallet.user,
            title=title,
            message=message
        )    

@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notify_{instance.user.id}",
            {
                "type": "send_notification",
                "message": NotificationSerializer(instance).data
            }
        )