from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from .models import Reserve,MealFood,Food, Meal,DailyMenu,Buffet,Organization,OrganizationMemberShipRequest,OrganizationMemberShipInvitation


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



class MenuSrializer(NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {
        'buffet_pk': 'buffet__pk'
    }

    date = serializers.DateField(source = 'dailymenu.date')
    class Meta :
        model = DailyMenu
        fields = ['id','date', 'created_at', 'updated_at']

class MealFoodSerializer(serializers.ModelSerializer):
    
    food = serializers.PrimaryKeyRelatedField(queryset= Food.objects.all(),many=False)

    price = serializers.DecimalField(source = 'mealfood.price',max_digits=10,decimal_places=0)
    number_in_stock = serializers.IntegerField(source = 'mealfood.number_in_stock')

    class Meta:
        model = MealFood
        fields = ['food','price','number_in_stock','id']

class MealSrializer(NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {
        'buffet_pk': 'dailyMenu__buffet__pk',
        'dailyMenu_pk':'dailyMenu__pk' 
    }
    meal_food = MealFoodSerializer(many=True)
    name = serializers.CharField(source = 'meal.name')
    time = serializers.TimeField(source = 'meal.time')
    class Meta :
        model = Meal
        fields = ['id','dailyMenu','created_at', 'updated_at','time','name','meal_food']





class FoodSerializer(serializers.ModelSerializer):
    # mealfood = serializers.PrimaryKeyRelatedField(queryset = MealFood.objects.all(),many= False)


    class Meta:
        model  = Food
        fields = ['name', 'description']



class BuffetListSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Buffet
        fields = ['id','name',]



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


class ReserveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserve
        fields = ['id', 'client', 'meal_food']

