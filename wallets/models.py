from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()



class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user.username