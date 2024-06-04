from typing import Iterable
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
    wallet = models.DecimalField(max_digits=10, decimal_places=0,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.username
    
    def joined_buffets(self):
        return Buffet.objects.filter(organization__members=self)

class Organization(models.Model):
    # members ManyToMany
    # admin OneToOne
    name  = models.CharField(max_length=127,unique=True) 
    image = models.ImageField(upload_to='organizations/profile-image',validators=[validators.validate_file_size],null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name



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
    
    def __str__(self) -> str:
        return self.user.username
    




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
    
    def __str__(self) -> str:
        return self.client.user.username + _(" -> ") + self.organization.name
    
    def save(self, *args, **kwargs):
        if self.status == 'A' and self.organization.members.filter(id=self.client.id).exists() == False:
            self.organization.members.add(self.client)
        super().save(*args, **kwargs)

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
    
    def __str__(self) -> str:
        return self.organization.name + _(" invited ") + self.client.user.username


class Buffet(models.Model):
    name         = models.CharField(max_length=127)
    organization = models.ForeignKey(Organization,related_name='buffets',on_delete=models.CASCADE)
    # daily_menus FK with DailyMenu
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name+ _(" at ") + self.organization.name

class Rate(models.Model):
    RATE_CHOICES = (
        (1, _('Very Bad')),
        (2, _('Bad')),
        (3, _('Normal')),
        (4, _('Good')),
        (5, _('Very Good')),
    )
    
    client = models.ForeignKey(Client,on_delete=models.CASCADE,related_name='rates')
    buffet = models.ForeignKey(Buffet,on_delete=models.CASCADE,related_name='rates')
    rate   = models.PositiveSmallIntegerField(choices=RATE_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.client.user.username + _(" rated ") + self.buffet.name + _(" as ") + str(self.rate)



class DailyMenu(models.Model):
    buffet = models.ForeignKey(Buffet,related_name='daily_menus',on_delete=models.CASCADE)
    date = models.DateField()
    
    def __str__(self) -> str:
        return _("Menu at ") + self.buffet.name + _(" on ") + str(self.date)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Meal(models.Model):
    dailyMenu = models.ForeignKey(DailyMenu,related_name='meals',on_delete=models.CASCADE)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField()
    time = models.TimeField()
    
    def __str__(self) -> str:
        return self.name + _(": ") + self.dailyMenu.buffet.name + _(" at ") + str(self.time) 




class Food(models.Model):
    name = models.CharField(unique=True)
    description = models.TextField(blank=True, null=True)
    
    
    def __str__(self) -> str:
        return self.name

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MealFood(models.Model):
    meal = models.ForeignKey(Meal,on_delete=models.CASCADE,related_name='items')
    food = models.ForeignKey(Food,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    number_in_stock = models.IntegerField()

    # reservations :FK with Reserve

    # TODO add a unique constraint on meal and food
    def __str__(self) -> str:
        return self.food.name + str(self.number_in_stock) + _(" in stock at ") + self.meal.name



class Reserve (models.Model):
    client     = models.ForeignKey(Client,on_delete=models.CASCADE,related_name='reservations')
    meal_food  = models.ForeignKey(MealFood,on_delete=models.CASCADE,related_name='reservations')
    date       = models.DateField()
    buffet     = models.ForeignKey(Buffet,on_delete=models.CASCADE,related_name='reservations',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    
    def __str__(self) -> str:
        return self.client.user.username + _(" reserved ") + self.meal_food.food.name + _(" at ") + self.meal_food.meal.name
    
    def save(self, *args, **kwargs):
        self.date = self.meal_food.meal.dailyMenu.date
        self.buffet = self.meal_food.meal.dailyMenu.buffet
        super().save(*args, **kwargs)