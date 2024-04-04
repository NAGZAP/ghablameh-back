from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from food_reservation.models import Client
from django.contrib.auth.hashers import check_password
from food_reservation.serializers import UserSerializer
from food_reservation.organizations.serializers import OrganizationSerializer
from food_reservation.tokens import get_tokens

User = get_user_model()



class ClientChangePasswordSerializer(serializers.Serializer):
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
        username = attrs.get('username')
        password = attrs.get('password')
        user = User.objects.filter(username=username).first()
        if user and hasattr(user, 'client') and user.check_password(password):
            attrs['tokens'] = get_tokens(user)
            return attrs
        raise serializers.ValidationError('نام کاربری یا رمز عبور اشتباه است')
        
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['tokens'] = instance.pop('tokens')
        return ret

class ClientRegisterSerializer(serializers.ModelSerializer):


    birthdate = serializers.DateField()
    gender = serializers.ChoiceField(choices=Client.GENDER_CHOICES)
    
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
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    phone_number = serializers.CharField(source='user.phone_number')
    date_joined = serializers.DateTimeField(source='user.date_joined')
    organizations = OrganizationSerializer(many=True)
    class Meta:
        model = Client
        fields = ['id','image','gender','birthdate','first_name','last_name','username','email','phone_number','date_joined','organizations','created_at','updated_at']

