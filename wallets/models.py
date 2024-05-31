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
    
    def deposit(self, amount):
        self.balance += amount
        self.save()
        
        
        
class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    description = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.wallet.user.username + _(" transaction of ") + str(self.amount) + _(" at ") + str(self.created_at)
    
    
    
    
class Payment(models.Model):
    token = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='payments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.wallet.user.username + _(" payment of ") + str(self.amount) + _(" at ") + str(self.created_at)
    
    