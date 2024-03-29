from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Organization,OrganizationAdmin
from django.contrib.auth.hashers import check_password

User = get_user_model()


class OrganizationChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True,max_length=127)
    new_password = serializers.CharField(write_only=True,max_length=127)
    

    def validate_old_password(self,value):
        user = self.instance
        if not check_password(value,user.password):
            raise serializers.ValidationError('لطفا رمز پیشین را به درستی وارد کنید')  
        return value
    
    
    def update(self, instance, validated_data):
        user = instance
        new_password = validated_data.pop("new_password")
        
        user.set_password(new_password)
        user.save()
        
        return user

    

class OrganizationSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(max_length=127)
    
    
    def validate_admin_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("این نام کاربری قبلا استفاده شده است.")
        
    def validate_name(self, value):
        if Organization.objects.filter(name=value).exists():
            raise serializers.ValidationError("این نام قبلا استفاده شده است.")
        
    
    def get_admin_username(self, obj):
        return obj.admin.user.username if obj.admin else None

    def update_admin_username(self, instance, validated_data):
        admin_username = validated_data.get('admin_username')
        if admin_username:
            instance.admin.user.username = admin_username
            instance.admin.user.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['admin_username'] = self.get_admin_username(instance)
        return data

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        return self.update_admin_username(instance, validated_data)
    class Meta:
        model  = Organization
        fields = ['id','name','image','admin_username']
        

        

    
class OrganizationListSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model  = Organization
        fields = ['id','name']


class OrganizationLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=127)
    password = serializers.CharField(max_length=127)
    

    
class OrganizationAdminCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=127)
    password = serializers.CharField(write_only=True,max_length=127)
    organization_name = serializers.CharField(max_length=127)
    email = serializers.EmailField()
    
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

        
    
    