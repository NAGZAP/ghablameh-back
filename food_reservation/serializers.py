from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Buffet,Organization,OrganizationMemberShipRequest,OrganizationMemberShipInvitation


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



class MemberShipRequestSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.user.username', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model  = OrganizationMemberShipRequest
        fields = ['id','client_name', 'organization_name', 'status', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        # if the request is accepted, add the client to the organization    
        if validated_data['status'] == 'A':
            instance.organization.members.add(instance.client)
        return super().update(instance, validated_data)


class CreateMemberShipRequestSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.user.username', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model  = OrganizationMemberShipRequest
        fields = ['id', 'organization', 'created_at', 'updated_at', 'client_name', 'organization_name']

    def save(self, **kwargs):
        return super().save(**kwargs)
    
    # TODO validate that the client is not already a member of the organization

    def create(self, validated_data):
        request = OrganizationMemberShipRequest.objects.filter(
            client=validated_data['client'], organization=validated_data['organization']
        ).first()
        if request:
            return request
        return super().create(validated_data)


class MemberShipInvitationSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.user.username', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model  = OrganizationMemberShipInvitation
        fields = ['id','client','client_name', 'organization', 'organization_name', 'status', 'created_at', 'updated_at']