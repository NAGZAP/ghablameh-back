from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import *


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model  = User
        fields = ['first_name','last_name','username','email','phone_number','date_joined']
        
        
        
class BuffetSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    average_rate = serializers.SerializerMethodField()
    number_of_rates = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField('get_image_url')


    # get the image of organization
    def get_image_url(self, obj):
        if obj.organization.image:
            return obj.organization.image.url
        return None


    def get_number_of_rates(self, obj):
        return Rate.objects.filter(buffet=obj).count()


    def get_average_rate(self, obj):
        rates = Rate.objects.filter(buffet=obj)
        if rates.exists():
            return rates.aggregate(models.Avg('rate'))['rate__avg']
        return None

    class Meta:
        model  = Buffet
        fields = ['id', 'name', 'created_at', 'updated_at', 'organization_name', 'average_rate', 'number_of_rates','image']




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
        fields = ['id', 'organization', 'created_at', 'updated_at', 'client_name', 'organization_name','status']
        read_only_fields = ['client','created_at','updated_at','status']
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



class RateSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.user.username', read_only=True)
    buffet_name = serializers.CharField(source='buffet.name', read_only=True)


    class Meta:
        model  = Rate
        fields = ['id','client','client_name', 'buffet', 'buffet_name', 'rate', 'created_at', 'updated_at']
        read_only_fields = ['client','buffet','created_at','updated_at']

    # if client already rated the buffet, update the rate
    def create(self, validated_data):
        rate = Rate.objects.filter(client=validated_data['client'], buffet=validated_data['buffet_id']).first()
        if rate:
            rate.rate = validated_data['rate']
            rate.save()
            return rate
        return super().create(validated_data)




class MealSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Meal
        fields = ['id','name','time']
    

class FoodSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Food
        fields = ['id','name','description']


class ReserveSerializer(serializers.ModelSerializer):
    meal = MealSerializer(source='meal_food.meal', read_only=True)
    buffet    = BuffetSerializer(source='meal_food.meal.dailyMenu.buffet', read_only=True)
    food = FoodSerializer(source='meal_food.food', read_only=True)

    class Meta:
        model  = Reserve
        fields = ['id','client','meal','buffet','food','created_at','updated_at']
        read_only_fields = ['id','meal','buffet','food','created_at','updated_at']