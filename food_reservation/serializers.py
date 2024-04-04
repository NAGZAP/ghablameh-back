from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Buffet


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model  = User
        fields = ['first_name','last_name','username','email','phone_number','date_joined']
        
        
        
class BuffetSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model  = Buffet
        fields = ['id', 'name', 'created_at', 'updated_at', 'organization_name']



class BuffetListSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Buffet
        fields = ['id','name']