from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Organization,OrganizationAdmin, Buffet,Client
from django.contrib.auth.hashers import check_password
from rest_framework.validators import UniqueValidator

User = get_user_model()



#org
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
    admin_username = serializers.CharField(max_length=127, required=False)
    name = serializers.CharField(max_length=127, required=False)

    def validate_name(self, value):
        print("validating name")
        print(self.instance.name)
        if self.instance.name == value:
            return value
        
        if Organization.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"The name '{value}' is already in use.")
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



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model  = User
        fields = ['first_name','last_name','username','email','phone_number','date_joined']

class OrganizationAdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    organization = OrganizationSerializer()
    
    class Meta:
        model  = OrganizationAdmin
        fields = ['id','user','organization','created_at','updated_at','role']



#client

class ClientChangePasswordSerializer(serializers.Serializer):
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

class ClientUpdateSerializer(serializers.ModelSerializer):
   
    birthdate = serializers.DateField()
    gender = serializers.CharField(max_length=1)

    def update(self, instance, validated_data):
        gender = validated_data.pop('gender',instance.gender)
        birthdate = validated_data.pop('birthdate',instance.birthdate)
        instance.gender = gender
        instance.birthdate = birthdate

        instance = super().update(instance.user, validated_data)
        instance.save()

        return instance
    
    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','phone_number','date_joined','gender','birthdate']

        
class ClientLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=127)
    password = serializers.CharField(max_length=127)

    def validate(self, attrs):
        return super().validate(attrs)



class ClientRegisterSerializer(serializers.ModelSerializer):


    birthdate = serializers.DateField()
    gender = serializers.CharField(max_length=1)
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        gender = validated_data.pop('gender')
        birthdate = validated_data.pop('birthdate')
        with transaction.atomic():
            user = User.objects.create(**validated_data)
            user.set_password(password)
            user.save()
            client  = Client.objects.create(user=user,gender=gender,birthdate=birthdate)
    
        return client
    
    class Meta:
        model  = User
        fields = ('username', 'password','gender','birthdate', 'email', 'first_name', 'last_name','phone_number')


class ClientSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    organizations = OrganizationSerializer(many=True)
    class Meta:
        model = Client
        fields = '__all__'



class BuffetSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Buffet
        fields = '__all__'



class BuffetListSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Buffet
        fields = ['id','name']
