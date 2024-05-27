from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
User = get_user_model()



@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['id','username', 'email', 'first_name', 'last_name', 'is_verified']
    list_editable = ['is_verified']

