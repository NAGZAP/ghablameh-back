from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Organization,OrganizationAdmin

User = get_user_model()


    
class OrganizationAdminCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    organization_name = serializers.CharField(max_length=150)
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("این نام کاربری قبلا استفاده شده است.")
        return value

    def validate_organization_name(self, value):
        if Organization.objects.filter(name=value).exists():
            raise serializers.ValidationError("این نام قبلا استفاده شده است.")
        return value
    
    
    def create(self, validated_data):
        org_name = validated_data.pop('organization_name')
        password = validated_data.pop('password')

        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            user.set_password(password)
            user.save()
            org = Organization.objects.create(name=org_name)
            org_admin = OrganizationAdmin.objects.create(organization=org, user=user)
            
        return org_admin

        
    
    