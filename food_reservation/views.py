from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from rest_framework.decorators import action 
from .permissions import *
from .tokens import get_tokens
from .models import (Organization,Client,Buffet)
from rest_framework.pagination import PageNumberPagination
from food_reservation.clients.serializers import *
from food_reservation.organizations.serializers import *
from .serializers import *
from ErrorCode import *
import json

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

class DailyMenuViewSet(mixins.ListModelMixin,GenericViewSet):
    serializer_class = MenuSrializer

    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            return [IsClientOrOrganizationAdmin()]
        else:
            return [IsOrganizationAdmin()]
    
           
class MealViewSet(ModelViewSet):
    serializer_class = MealSrializer

    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            return [IsClientOrOrganizationAdmin()]
        else:
            return [IsOrganizationAdmin()]


class MealFoodViewSet(ModelViewSet):
    serializer_class = MealFoodSerializer

    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            return [IsClientOrOrganizationAdmin()]
        else:
            return [IsOrganizationAdmin()]




class FoodViewSet(ModelViewSet):
    serializer_class = FoodSerializer

    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            return [IsClientOrOrganizationAdmin()]
        else:
            return [IsOrganizationAdmin()]
        
    def get_serializer_class(self):
        
        return FoodSerializer
        

    def get_queryset(self):
        return Food.objects.all()
        
            
    def perform_create(self, serializer):
        body = self.request.body.decode('utf-8')
        body_ready = json.load(body)
        exist = Food.objects.get(name = body_ready['name'])
        if exist :
            return Response({'message':'this food found in database '},status=200)  
        else :
            serializer.save(name = body_ready['name'])

    def perform_update(self, serializer):
        body = self.request.body.decode('utf-8')
        body_ready = json.load(body)
        exist = Food.objects.get(name = body_ready['name'])
        if exist :
            
            serializer.save(name = body_ready['name'])  
        else :
            return Response({'message':'this food not found in data bese try to create a new one '},status=200)
            


class ReserveViewSet(ModelViewSet):
    queryset = Reserve.objects.all()
    serializer_class = ReserveSerializer

    def create(self, request, *args, **kwargs):
        client = request.user.client
        
        # Retrieve data from request
        meal_food_id = request.data.get('meal_food')
        
        # Check if the meal_food exists
        try:
            meal_food = MealFood.objects.get(pk=meal_food_id)
        except MealFood.DoesNotExist:
            return Response({"error": "MealFood does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the client is a member of the organization and buffet
        if client not in meal_food.meal.dailyMenu.buffet.organization.members.all():
            return Response({"error": "Client is not a member of the organization and buffet"}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if the client has already reserved food in this buffet, daily menu, and meal
        existing_reservation = Reserve.objects.filter(client=client, meal_food__meal__dailyMenu__buffet=meal_food.meal.dailyMenu.buffet, meal_food__meal__dailyMenu=meal_food.meal.dailyMenu, meal_food__meal=meal_food.meal).exists()
        if existing_reservation:
            return Response({"error": "Client has already reserved food in this buffet, daily menu, and meal"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if there is enough stock
        if meal_food.number_in_stock <= 0:
            return Response({"error": "Not enough stock available"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if client has enough balance
        if client.wallet < meal_food.price:
            return Response({"error": "Insufficient balance in client's wallet"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the reservation
        reserve = Reserve.objects.create(client=client, meal_food=meal_food)
        
        # Update client's wallet and meal_food's stock
        client.wallet -= meal_food.price
        client.save()
        meal_food.number_in_stock -= 1
        meal_food.save()
        
        serializer = ReserveSerializer(reserve)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        client = request.user.client
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Retrieve data from request
        meal_food_id = request.data.get('meal_food')
        
        # Check if the meal_food exists
        try:
            meal_food = MealFood.objects.get(pk=meal_food_id)
        except MealFood.DoesNotExist:
            return Response({"error": "MealFood does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the client is a member of the organization and buffet
        if client not in meal_food.meal.dailyMenu.buffet.organization.members.all():
            return Response({"error": "Client is not a member of the organization and buffet"}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if the client has already reserved food in this buffet, daily menu, and meal
        existing_reservation = Reserve.objects.exclude(pk=instance.pk).filter(client=client, meal_food__meal__dailyMenu__buffet=meal_food.meal.dailyMenu.buffet, meal_food__meal__dailyMenu=meal_food.meal.dailyMenu, meal_food__meal=meal_food.meal).exists()
        if existing_reservation:
            return Response({"error": "Client has already reserved food in this buffet, daily menu, and meal"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if there is enough stock
        if meal_food.number_in_stock <= 0:
            return Response({"error": "Not enough stock available"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if client has enough balance
        if client.wallet < meal_food.price:
            return Response({"error": "Insufficient balance in client's wallet"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the reservation
        instance.meal_food = meal_food
        instance.save()
        
        # Update client's wallet and meal_food's stock
        client.wallet -= meal_food.price
        client.save()
        meal_food.number_in_stock -= 1
        meal_food.save()
        
        serializer = ReserveSerializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # Retrieve the reservation
        reservation = self.get_object()
        
        # Check if the client owns the reservation
        if request.user.client != reservation.client:
            return Response({"error": "You are not authorized to perform this action"}, status=status.HTTP_403_FORBIDDEN)
        
        # Update client's wallet and meal_food's stock
        reservation.client.wallet += reservation.meal_food.price
        reservation.client.save()
        reservation.meal_food.number_in_stock += 1
        reservation.meal_food.save()
        
        # Delete the reservation
        self.perform_destroy(reservation)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        # Retrieve client's reservations
        reservations = Reserve.objects.filter(client=request.user.client)
        serializer = ReserveSerializer(reservations, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if the client owns the reservation
        if request.user.client != instance.client:
            return Response({"error": "You are not authorized to view this reservation"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ReserveSerializer(instance)
        return Response(serializer.data)    


class OrganizationViewSet(
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Organization.objects.all()
    
    def get_serializer_class(self):
        action = self.action
        
        if action == 'list':
            return OrganizationListSerializer
        if action == 'register':
            return OrganizationAdminCreateSerializer
        if action == 'me':
            return OrganizationSerializer
        if action == 'password':
            return OrganizationChangePasswordSerializer
        if action == 'members':
            ClientListSerializer
    
    def get_permissions(self):
        if self.action in ['me', 'password','members']:
            return [IsOrganizationAdmin()]
        else:
            return []

    





    
                
    @action(['POST'] , False)
    def register(self,request):
        serializer = OrganizationAdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin_user = serializer.save()
        
        return Response({
            "admin_user":OrganizationAdminSerializer(admin_user).data,
            'tokens' : get_tokens(admin_user.user),
        },status=status.HTTP_201_CREATED)
    
        
        
    @action(['GET','PUT'] , False)
    def me(self,request):
        instance = request.user.organization_admin.organization

        if request.method == 'GET':
            serializer = OrganizationSerializer(instance)
        if request.method == 'PUT':
            serializer = OrganizationSerializer(instance,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)

            
    @action(['POST'] , False)
    def password(self,request):
        serializer = OrganizationChangePasswordSerializer(request.user,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response( {'message' : 'رمز با موفقیت تغییر یافت'} ,status= status.HTTP_200_OK)
    
    
    @action(['GET'] , False)
    def members(self,request):
        org = request.user.organization_admin.organization
        serializer = ClientListSerializer(org.members.all(),many=True)
        return Response(serializer.data)


class ClientViewSet(GenericViewSet):
    def get_serializer_class(self):
        action = self.action
        if action == 'register':
            return ClientRegisterSerializer
        if action == 'me':
            return ClientSerializer           
        if action == 'password':
            return ClientChangePasswordSerializer

    def get_permissions(self):
        if self.action in ['me', 'password','my_organizations']:
            return [IsClient(),IsNotOrganizationAdmin()]
        else:
            return []


    @action(['POST'] , False)
    def register(self, request):

        serializer = ClientRegisterSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        client = serializer.save()

        return Response({
            **ClientSerializer(client).data,
            'tokens' : get_tokens(client.user),
        },status=status.HTTP_201_CREATED)

    @action(['GET','PUT'] , False)
    def me(self,request):
        instance = request.user.client
        if request.method == 'PUT':
            serializer = ClientSerializer(instance,data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

        serializer = ClientSerializer(instance)
        return Response(serializer.data)

    @action(['POST'] , False)
    def password(self,request):

        serializer = ClientChangePasswordSerializer(request.user,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response( {'message' : 'رمز با موفقیت تغییر یافت'} ,status= status.HTTP_200_OK)
    

    @action(['GET'],False)
    def my_organizations(self,request):
        instance = request.user.client.organizations.all()
        serializer = ClientOrgSerializer(instance,many=True)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)

class ClientMembershipRequestViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = CreateMemberShipRequestSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return OrganizationMemberShipRequest.objects.filter(
            client_id=self.request.user.client.id
        )

    def perform_create(self, serializer):
        serializer.save(client=self.request.user.client, status="P")


class OrgMembershipRequestViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    serializer_class = MemberShipRequestSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        return OrganizationMemberShipRequest.objects.filter(
            organization=self.request.user.organization_admin.organization
        )


    def perform_update(self, serializer):
        serializer.save(
            organization=self.request.user.organization_admin.organization
        )


class BuffetViewSet(ModelViewSet):

    serializer_class = BuffetSerializer

    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            return [IsClientOrOrganizationAdmin()]
        else:
            return [IsOrganizationAdmin()]
        
    def get_serializer_class(self):
        if self.action in ['list']:
            return BuffetListSerializer
        return BuffetSerializer
        

    def get_queryset(self):
        # Organization Admin
        if hasattr(self.request.user,'organization_admin'):
            org = self.request.user.organization_admin.organization
            return Buffet.objects.filter(organization=org).all()
        # Client
        return Buffet.objects.filter(
            organization__in=self.request.user.client.organizations.all())\
            .all()
            
    def perform_create(self, serializer):
        org = self.request.user.organization_admin.organization
        serializer.save(organization=org)

    def perform_update(self, serializer):
        org = self.request.user.organization_admin.organization
        serializer.save(organization=org)


class AllOrgListViewSet(mixins.ListModelMixin,
    GenericViewSet,):
    serializer_class = OrganizationListSerializer
    queryset = Organization.objects.all()
    pagination_class = StandardResultsSetPagination