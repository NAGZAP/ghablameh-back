from django.contrib import admin
from .models import User



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone_number', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email', 'phone_number']
    ordering = ['username']
    actions = ['make_staff', 'make_active', 'make_inactive']
    
    def make_staff(self, request, queryset):
        queryset.update(is_staff=True)
    
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    
    make_staff.short_description = "Make selected users staff"
    make_active.short_description = "Make selected users active"
    make_inactive.short_description = "Make selected users inactive"