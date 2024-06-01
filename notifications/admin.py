from django.contrib import admin
from .models import Notification




@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'created_at', 'read']
    list_filter = ['read']
    search_fields = ['title', 'message']
    ordering = ['-created_at']
    actions = ['mark_as_read', 'mark_as_unread']
    # autocomplete_fields = ['user']

    list_select_related = ['user']

    
    def mark_as_read(self, request, queryset):
        queryset.update(read=True)
    
    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)