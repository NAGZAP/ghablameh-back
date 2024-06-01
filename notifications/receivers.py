from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from .models import Notification

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
    elif sender.__name__ == 'Payment' and instance.verified:
        Notification.objects.create(
            user=instance.user,
            title=_(f"Payment Received"),
            message=_(f"Your payment of {instance.amount} in {instance.created_at} has been received.")
        )
