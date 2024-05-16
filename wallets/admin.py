from django.contrib import admin
from .models import Wallet 



@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at', 'updated_at']
    search_fields = ['user__username']
    ordering = ['created_at']
    actions = ['zero_balance']
    
    def zero_balance(self, request, queryset):
        queryset.update(balance=0)
        self.message_user(request, "Balance of selected wallets has been set to zero.")
    zero_balance.short_description = "Set balance to zero"
    