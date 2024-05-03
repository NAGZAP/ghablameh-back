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




class OrganizationMemberShipRequest(models.Model):
    STATUS_CHOICES = (
        ('P', _('Pending')),
        ('A', _('Accepted')),
        ('R', _('Rejected')),
    )
    
    client       = models.ForeignKey(Client,on_delete=models.CASCADE,related_name='membership_requests') 
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,related_name='membership_requests')
    status       = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class OrganizationMemberShipInvitation(models.Model):
    STATUS_CHOICES = (
        ('P', _('Pending')),
        ('A', _('Accepted')),
        ('R', _('Rejected')),
    )
    
    client       = models.ForeignKey(Client,on_delete=models.CASCADE,related_name='membership_invitations') 
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,related_name='membership_invitations')
    status       = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Buffet(models.Model):
    name         = models.CharField(max_length=127)
    organization = models.ForeignKey(Organization,related_name='buffets',on_delete=models.CASCADE)
    # daily_menus FK with DailyMenu
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    



class DailyMenu(models.Model):
    buffet = models.ForeignKey(Buffet,related_name='daily_menus',on_delete=models.CASCADE)
    date = models.DateField()


class Meal(models.Model):
    dailyMenu = models.ForeignKey(DailyMenu,related_name='meals',on_delete=models.CASCADE)
    name = models.CharField()
    time = models.TimeField()

class Food(models.Model):
    name = models.CharField()
    description = models.TextField()


class MealFood(models.Model):
    meal = models.ForeignKey(Meal,on_delete=models.CASCADE)
    food = models.ForeignKey(Food,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    number_in_stock = models.IntegerField()

    # reservations :FK with Reserve

    # TODO add a unique constraint on meal and food



class Reserve (models.Model):
    client = models.ForeignKey(Client,on_delete=models.CASCADE,related_name='reservations')
    meal_food = models.ForeignKey(MealFood,on_delete=models.CASCADE,related_name='reservations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)