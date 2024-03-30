from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    # client OneToOneField
    # admin OneToOne field

    phone_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{12,15}$',
                message="شماره تلفن باید به شکل +989123456789 وارد شود"
            ),
        ],
        blank=True,
        null=True
    )