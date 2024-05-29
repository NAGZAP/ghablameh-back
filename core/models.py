from typing import Iterable
import random
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.core.mail import send_mail
from django.conf import settings

SENDER_EMAIL = settings.EMAIL_HOST_USER


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
        null=True,
        unique=True
    )
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    
class EmailVerification(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='email_verification')
    code = models.CharField(max_length=5,null=True,blank=True)
    expire_at = models.DateTimeField(null=True,blank=True)

    
    def __str__(self):
        return self.user.username
    
    def is_expired(self):
        return self.expire_at < timezone.now()
    
    def is_valid(self,code):
        return self.code == code and not self.is_expired()
    
    def generate_code(self):
        return ''.join([str(random.randint(0,9)) for _ in range(5)])
    

    
    def send_verification_email(self):
        self.code = self.generate_code()
        self.expire_at = timezone.now() + timedelta(minutes=10)
        self.save()
        send_mail(
            'کد تایید ایمیل',
            f'کد تایید شما: {self.code}',
            SENDER_EMAIL,
            [self.user.email],
            fail_silently=False)
        

class ForgetPasswordVerification(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='forget_password_verification')
    code = models.CharField(max_length=5,null=True,blank=True)
    expire_at = models.DateTimeField(null=True,blank=True)

    
    def __str__(self):
        return self.user.username
    
    def is_expired(self):
        return self.expire_at < timezone.now()
    
    def is_valid(self,code):
        return self.code == code and not self.is_expired()
    
    def generate_code(self):
        return ''.join([str(random.randint(0,9)) for _ in range(5)])
    

    
    def send_verification_email(self):
        self.code = self.generate_code()
        self.expire_at = timezone.now() + timedelta(minutes=10)
        self.save()
        send_mail(
            'کد بازیابی رمز عبور',
            f'کد بازیابی رمز عبور شما: {self.code}',
            SENDER_EMAIL,
            [self.user.email],
            fail_silently=False)
            
            