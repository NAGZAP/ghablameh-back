from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from . import validators


class Client(models.Model):
    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
    )
    
    user          = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='client') 
    gender        = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    birthdate     = models.DateField(null=True, blank=True)
    organizations = models.ManyToManyField('Organization',related_name="members")
    image         = models.ImageField(upload_to='clients/profile-image',validators=[validators.validate_file_size],null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Organization(models.Model):
    # members ManyToMany
    # admin OneToOne
    name  = models.CharField(max_length=127,unique=True) 
    image = models.ImageField(upload_to='organizations/profile-image',validators=[validators.validate_file_size],null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    



class OrganizationAdmin(models.Model):
    ROLE_CHOICES = (
        ('O', _('Owner')),
        ('M', _('Manager')),
        ('A', _('Admin')),
        ('R', _('Reporter')),
    )
    
    user         = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='organization_admin') 
    organization = models.OneToOneField(Organization,on_delete=models.CASCADE,related_name='admin')
    role         = models.CharField(max_length=1, choices=ROLE_CHOICES, default='O')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    



class Buffet(models.Model):
    name         = models.CharField(max_length=127)
    organization = models.ForeignKey(Organization,related_name='buffets',on_delete=models.CASCADE)
    # TODO: implement here later 
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
