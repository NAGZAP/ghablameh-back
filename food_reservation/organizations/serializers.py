from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from food_reservation.models import Organization,OrganizationAdmin
from django.contrib.auth.hashers import check_password
from food_reservation.serializers import UserSerializer

User = get_user_model()




class OrganizationChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True,max_length=127)
    new_password = serializers.CharField(write_only=True,max_length=127)
    

    def validate_old_password(self,value):
        user = self.instance
        if not check_password(value,user.password):
            raise serializers.ValidationError('لطفا رمز پیشین را به درستی وارد کنید')  
        return value
    
    def validate_new_password(self, value):
        validate_password(value)
        return value
        
    
    def update(self, instance, validated_data):
        user = instance
        new_password = validated_data.pop("new_password")
        
        user.set_password(new_password)
        user.save()
        
        return user

class OrganizationSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(max_length=127, required=False)
    name = serializers.CharField(max_length=127, required=False)

    def validate_name(self, value):
        if self.instance.name == value:
            return value
        if Organization.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"این نام سازمان '{value}' قبلا استفاده شده است.")
        return value
    
    def validate_admin_username(self, value):
        if self.instance.admin.user.username == value:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(f"این نام کاربری '{value}' قبلا استفاده شده است.")
        return value
        
    

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
        model = Organization
        fields = ['id', 'name', 'image', 'admin_username']

    
class OrganizationListSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model  = Organization
        fields = ['id','name']


class OrganizationLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=127)
    password = serializers.CharField(max_length=127)


    def validate(self, attrs):
        # check username password
        return super().validate(attrs)
    

    
class OrganizationAdminCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=127)
    password = serializers.CharField(write_only=True,max_length=127)
    organization_name = serializers.CharField(max_length=127)
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(f"{value} کاربری قبلا استفاده شده است.")
        return value

    def validate_organization_name(self, value):
        if Organization.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"{value} قبلا استفاده شده است.")
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
    
    class Meta:
        model  = User
        fields = ('organization_name','username', 'password', 'email', 'first_name', 'last_name','phone_number')



class OrganizationAdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    organization = OrganizationSerializer()
    
    class Meta:
        model  = OrganizationAdmin
        fields = ['id','user','organization','created_at','updated_at','role']

