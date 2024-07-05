from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from .models import *


User = get_user_model()






class ClientSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    phone_number = serializers.CharField(source='user.phone_number')
    date_joined = serializers.DateTimeField(source='user.date_joined',read_only=True)
    image_base64 = serializers.CharField(required=False,write_only=True)
    image_url = serializers.SerializerMethodField('get_image_url')
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
    class Meta:
        model = Client
        fields = ['id','image_base64','image_url','gender','birthdate','first_name','last_name','username','email','phone_number','date_joined','created_at','updated_at']
        
    
    def validate_image_base64(self,value):
        if value is not None:
            try:
                format, imgstr = value.split(';base64,') 
                ext = format.split('/')[-1] 
                base64.b64decode(imgstr)
            except:
                raise serializers.ValidationError('عکس نامعتبر است')
        return value
        
    
    def update(self, instance, validated_data):
        user = instance.user
        user_data = validated_data.pop('user',{})
        user.first_name = user_data.get('first_name',user.first_name)
        user.last_name = user_data.get('last_name',user.last_name)
        user.username = user_data.get('username',user.username)
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
    
    def validate_username(self,value):
        if self.instance.user.username != value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError('نام کاربری تکراری است')
        return value
    
    def validate_email(self,value):
        if self.instance.user.email != value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError('ایمیل تکراری است')
        return value
    
    def validate_phone_number(self,value):
        if self.instance.user.phone_number != value and User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError('شماره تلفن تکراری است')
        return value

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



class MenuSerializer(NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {
        'buffet_pk': 'buffet__pk'
    }

    date = serializers.DateField()
    class Meta :
        model = DailyMenu
        fields = ['id','date', 'created_at', 'updated_at']

class SimpleMealFoodSerializer(serializers.ModelSerializer):
    
    food = serializers.PrimaryKeyRelatedField(queryset= Food.objects.all(),many=False)

    price = serializers.DecimalField(max_digits=10,decimal_places=0)
    number_in_stock = serializers.IntegerField()

    class Meta:
        model = MealFood
        fields = ['food','price','number_in_stock','id']



class BuffetListSerializer(serializers.ModelSerializer):

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
    client = ClientSerializer(read_only=True)
    class Meta:
        model  = OrganizationMemberShipRequest
        fields = ['id','client_name', 'client', 'organization_name', 'status', 'created_at', 'updated_at']



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



    

class FoodSerializer(serializers.ModelSerializer):
    
        class Meta:
            model  = Food
            fields = ['id','name','description']

    
class SimpleMealSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Meal
        fields = ['id','name','time']

class MealFoodSerializer(serializers.ModelSerializer):
    food = FoodSerializer(read_only=True)
    
    class Meta:
        model  = MealFood
        fields = ['id','food','price','number_in_stock']
        read_only_fields = ['id','food']
        
        
    def validate(self, attrs):
        if attrs['number_in_stock'] < 0:
            raise serializers.ValidationError("number_in_stock must be positive")
        user = self.context.get('user')
        if not hasattr(user,'organization_admin'):
            raise serializers.ValidationError("You are not an admin")
        buffet_id = self.context.get('buffet_id')
        buffet = user.organization_admin.organization.buffets.filter(id=buffet_id).first()
        if not buffet:
            raise serializers.ValidationError("Buffet not found")
        menu_date = self.context.get('menu_date')
        daily_menu = buffet.daily_menus.filter(date=menu_date).first()
        if not daily_menu:
            raise serializers.ValidationError("Daily menu not found")
        meal_id = self.context.get('meal_id')
        meal = daily_menu.meals.filter(id=meal_id).first()
        if not meal:
            raise serializers.ValidationError("Meal not found")
        return attrs
    
class MealFoodCreateUpdateSerializer(MealFoodSerializer):
    food = serializers.PrimaryKeyRelatedField(queryset= Food.objects.all(),many=False)
    
    class Meta:
        model  = MealFood
        fields = ['id','food','price','number_in_stock']
        read_only_fields = ['id']
        


class MealSerializer(serializers.ModelSerializer):
    items = MealFoodSerializer(many=True, read_only=True)
    
    class Meta:
        model  = Meal
        fields = ['id','name','time','items','created_at','updated_at']
        read_only_fields = ['id','items','created_at','updated_at']  


        
class DailyMenuSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True, read_only=True)

    class Meta:
        model  = DailyMenu
        fields = ['id','date','meals']
        read_only_fields = ['id','date','meals']   
        
        
class ReserveSerializer(serializers.ModelSerializer):
    meal_food = MealFoodSerializer(read_only=True)
    buffet = BuffetSerializer(read_only=True)

    
    class Meta:
        model  = Reserve
        fields = ['id','meal_food','buffet','created_at','updated_at']
        read_only_fields = ['id','meal_food','buffet','created_at','updated_at']


class ReserveCreateUpdateSerializer(serializers.ModelSerializer):
    meal_food = serializers.PrimaryKeyRelatedField(queryset= MealFood.objects.all(),many=False)
    
    class Meta:
        model  = Reserve
        fields = ['id','meal_food']

    def validate(self, attrs):
        # check that the client have access to this meal food in its buffets?
        user = self.context.get('user')
        if not hasattr(user,'client'):
            raise serializers.ValidationError(_("You are not a client"))
        joined_buffets = user.client.joined_buffets()
        buffet = attrs['meal_food'].meal.dailyMenu.buffet
        if not buffet in joined_buffets:
            raise serializers.ValidationError(_("You are not allowed to reserve this meal food"))
        # check that the meal food is in stock
        meal_food = attrs['meal_food']
        if not meal_food.number_in_stock > 0:
            raise serializers.ValidationError(_("This meal food is out of stock"))
        
        # check that client don't have 2 reserve on same meal 
        if user.client.reservations.filter(meal_food__meal=meal_food.meal).exists():
            raise serializers.ValidationError(_("You already have a reserve on this meal"))
        
        if not user.check_balance(meal_food.price):
            raise serializers.ValidationError(_("Not enough balance"))
        
        return attrs