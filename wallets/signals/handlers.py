import logging
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from wallets.models import Wallet
logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
        logger.info(f"Wallet created for user {instance.username}")