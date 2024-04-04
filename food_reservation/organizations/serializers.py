import base64
import uuid
from django.core.files.base import ContentFile
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from food_reservation.models import Organization,OrganizationAdmin
from django.contrib.auth.hashers import check_password
from food_reservation.serializers import UserSerializer
from food_reservation.tokens import get_tokens

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
    admin_username = serializers.CharField(source='admin.user.username')
    admin_first_name = serializers.CharField(source='admin.user.first_name')
    admin_last_name = serializers.CharField(source='admin.user.last_name')
    admin_email = serializers.EmailField(source='admin.user.email')
    admin_phone_number = serializers.CharField(source='admin.user.phone_number')
    image_base64 = serializers.CharField(write_only=True)
    image_url = serializers.CharField(source='image.url',read_only=True)
    
    
    def validate_admin_username(self, value):
        if self.instance.admin.user.username != value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError(f"{value} کاربری قبلا استفاده شده است.")
        return value
    
    def validate_admin_email(self, value):
        if self.instance.admin.user.email != value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError(f"{value} ایمیل قبلا استفاده شده است.")
        return value
    
    def validate_admin_phone_number(self, value):
        if self.instance.admin.user.phone_number != value and User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(f"{value} شماره تلفن قبلا استفاده شده است.")
        return value
    
    
    def update(self, instance, validated_data):
        user = instance.admin.user
        user_data = validated_data.pop('admin').pop('user')
        user.username = user_data.get('username',user.username)
        user.first_name = user_data.get('first_name',user.first_name)
        user.last_name = user_data.get('last_name',user.last_name)
        user.email = user_data.get('email',user.email)
        user.phone_number = user_data.get('phone_number',user.phone_number)
        user.save()
        
        image_data = validated_data.pop('image_base64',None)
        if image_data is not None:
            if image_data is not None:
                format, imgstr = image_data.split(';base64,') 
                ext = format.split('/')[-1] 
                data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
                instance.image.save(data.name, data, save=True)

            
        
        super().update(instance, validated_data)
        return instance    
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'image_base64','image_url', 'admin_username', 'admin_first_name', 'admin_last_name', 'admin_email', 'admin_phone_number', 'created_at', 'updated_at']

    
class OrganizationListSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model  = Organization
        fields = ['id','name']


class OrganizationLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=127)
    password = serializers.CharField(max_length=127)


    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            if hasattr(user, 'organization_admin'):
                attrs['tokens'] = get_tokens(user)
                return attrs
            else:
                raise serializers.ValidationError('امکان لاگین به عنوان ادمین سازمان وجود ندارد')
        raise serializers.ValidationError('نام کاربری یا رمز عبور اشتباه است')


    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['tokens'] = instance.pop('tokens')
        return ret
    
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

