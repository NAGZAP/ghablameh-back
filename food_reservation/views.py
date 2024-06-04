from datetime import datetime
import logging
from django.db.models.functions import Coalesce
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from .permissions import *
from .models import (Organization,Client,Buffet)
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from core.models import EmailVerification
from food_reservation.clients.serializers import *
from food_reservation.organizations.serializers import *
from .permissions import *
from .models import (Organization,Client,Buffet,Reserve)
from .serializers import *
from .paginations import *
from .filters import *
from ErrorCode import *
import json
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)



class WeeklyMenuViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):  
    serializer_class = DailyMenuSerializer
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('from_date', openapi.IN_QUERY, description="Start date for the weekly menu", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        openapi.Parameter('to_date', openapi.IN_QUERY, description="End date for the weekly menu", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE)
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    
    def get_queryset(self):
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        buffet_pk = self.kwargs.get('buffet_pk')
        if not from_date or not to_date:
            return DailyMenu.objects.none()
        user = self.request.user
        joined_buffets = []
        if hasattr(user,'client'):
            joined_buffets = user.client.joined_buffets()
        elif hasattr(user,'organization_admin'):
            joined_buffets = user.organization_admin.organization.buffets.all()
        return DailyMenu.objects.filter(buffet__in=joined_buffets, buffet=buffet_pk,date__gte=from_date,date__lte=to_date)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsClientOrOrganizationAdmin()]
        else:
            return [IsOrganizationAdmin()]
        
    def perform_create(self, serializer):
        buffet_pk = self.kwargs.get('buffet_pk')
        serializer.save(buffet_id=buffet_pk)
        
    def perform_update(self, serializer):
        buffet_pk = self.kwargs.get('buffet_pk')
        serializer.save(buffet_id=buffet_pk)

            

class DailyMenuViewSet(
    mixins.RetrieveModelMixin,
    GenericViewSet
    ):
    lookup_field = 'date'
    serializer_class = DailyMenuSerializer
    permission_classes = [IsClientOrOrganizationAdmin]

    
    def get_queryset(self):
        date = self.kwargs.get('date')
        buffet_pk = self.kwargs.get('buffet_pk')
        user = self.request.user
        print(1)
        if hasattr(user,'organization_admin'):
            print(2)
            daily_menu =  DailyMenu.objects.get_or_create(buffet_id=buffet_pk, date=date)[0]
            return DailyMenu.objects.filter(buffet_id=buffet_pk, date=date)
        else:
            print(3)
            return DailyMenu.objects.filter(buffet_id=buffet_pk, date=date)



class MealViewSet(ModelViewSet):
    permission_classes = [IsOrganizationAdmin]
    serializer_class = SimpleMealSerializer
    
    def get_queryset(self):
        buffet_pk = self.kwargs.get('buffet_pk')
        menu_date = self.kwargs.get('menu_date')
        if menu_date:
            daily_menu = DailyMenu.objects.get_or_create(buffet_id=buffet_pk, date=menu_date)[0]
            return Meal.objects.select_related('dailyMenu').filter(dailyMenu__buffet_id=buffet_pk, dailyMenu__date=menu_date)
        return Meal.objects.none()




class MealFoodViewSet(ModelViewSet):
    permission_classes = [IsOrganizationAdmin]
        
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return MealFoodSerializer
        return MealFoodCreateUpdateSerializer
    
    def get_queryset(self):
        meal_pk = self.kwargs.get('meal_pk')
        return MealFood.objects.filter(meal_id=meal_pk)
    
    def perform_create(self, serializer):
        meal_pk = self.kwargs.get('meal_pk')
        serializer.save(meal_id=meal_pk)
        
    def perform_update(self, serializer):

        meal_pk = self.kwargs.get('meal_pk')
        serializer.save(meal_id=meal_pk)
        
    def get_serializer_context(self):
        # add the user, menu_date, buffet_pk and meal_pk to the context
        context = super().get_serializer_context()
        context['meal_id'] = self.kwargs.get('meal_pk')
        context['buffet_id'] = self.kwargs.get('buffet_pk')
        context['menu_date'] = self.kwargs.get('menu_date')
        context['user'] = self.request.user
        return context





class FoodViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
    ):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    permission_classes = [IsOrganizationAdmin]
    queryset = Food.objects.all()
    pagination_class = CustomPageNumberPagination
    serializer_class = FoodSerializer
    


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
            
        return OrganizationSerializer
    
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
        verification = EmailVerification.objects.create(user=admin_user.user)
        try:
            verification.send_verification_email()
        except Exception as e:
            logger.error(e)
            return Response({
                "message":"خطا در ارسال ایمیل تایید",
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({
            "admin_user":OrganizationAdminSerializer(admin_user).data,
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

        verification = EmailVerification.objects.create(user=client.user)
        try:
            verification.send_verification_email()
        except Exception as e:
            logger.error(e)
            return Response({
                "message":"خطا در ارسال ایمیل تایید",
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({
            **ClientSerializer(client).data,
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
    

class ClientOrganizationViewSet(
    mixins.ListModelMixin,
    GenericViewSet):
    permission_classes = [IsClient,IsNotOrganizationAdmin]
    serializer_class = OrganizationListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrganizationFilter
    
    def get_queryset(self):
        return self.request.user.client.organizations.all()\
            .prefetch_related('buffets','buffets__rates')\
            .annotate(
                average_rate=Coalesce(models.Avg('buffets__rates__rate'), 0.0)
            )\
            .order_by('-average_rate')
            
    

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
        if self.request.user.is_anonymous:
            return OrganizationMemberShipRequest.objects.none()
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
        if self.request.user.is_anonymous:
            return OrganizationMemberShipRequest.objects.none()
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
        elif self.action in ['top5']:
            return [IsClient()] 
        else:
            return [IsOrganizationAdmin()]
        

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Buffet.objects.none()
        # Organization Admin
        if hasattr(self.request.user,'organization_admin'):
            org = self.request.user.organization_admin.organization
            return Buffet.objects.filter(organization=org).all().select_related('organization')
        # Client
        return Buffet.objects.filter(
            organization__in=self.request.user.client.organizations.all())\
            .all().select_related('organization')
            
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
    pagination_class = CustomPageNumberPagination
    @action(['GET'],False)
    def top5(self,request):
        queryset = Buffet.objects.filter(
            organization__in=request.user.client.organizations.all()
        ).select_related('organization')\
            .prefetch_related('rates')\
            .annotate(
            average_rate=Coalesce(models.Avg('rates__rate'), 0.0)
        ).order_by('-average_rate')[:5]
        serializer = BuffetSerializer(queryset,many=True)
        return Response(serializer.data)


class BuffetsRateViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    """
    List, Create, Retrieve, Update Rates for Buffets

    If client already rated the buffet, update the rate

    If the client is not a member of the organization that owns the buffet, 404 is raised
    
    """
    serializer_class = RateSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        if self.request.user.is_anonymous or not Buffet.objects.filter(
            id=self.kwargs.get('buffet_pk'),
            organization__in=self.request.user.client.organizations.all()
        ).exists():
            return Rate.objects.none()
        
        return Rate.objects.filter(
            buffet_id=self.kwargs['buffet_pk'], client=self.request.user.client
        ).select_related('client','buffet','client__user')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['buffet_id'] = self.kwargs.get('buffet_pk')
        if self.request.user.is_authenticated:
            context['client_id'] = self.request.user.client.id
        return context
    
    

    def perform_create(self, serializer):
        serializer.save(client=self.request.user.client, buffet_id=self.kwargs['buffet_pk'])

    def perform_update(self, serializer):
        serializer.save(client=self.request.user.client, buffet_id=self.kwargs['buffet_pk'])



class ReservationViewSet(ModelViewSet):
    permission_classes = [IsClient]
    
    def get_serializer_class(self):
        action = self.action
        if action in ['list','retrieve','next']:
            return ReserveSerializer
        return ReserveCreateUpdateSerializer

    # TODO :add wallet decreasing
    @action(['GET'],False)
    def next(self,request):
        next_reserve = Reserve.objects.filter(
            client=request.user.client,
            date__gte=datetime.now().date()
        ).order_by('date').first()
        if not next_reserve:
            return Response({
                "message":"شما رزروی ندارید"
            },status=status.HTTP_404_NOT_FOUND)
        serializer = ReserveSerializer(next_reserve)
        return Response(serializer.data)

        

    def get_queryset(self):
        return Reserve.objects.filter(
            client=self.request.user.client
        ).select_related('client','client__user','meal_food')
    
    def perform_create(self, serializer):
        serializer.save(client=self.request.user.client)

    def perform_update(self, serializer):
        serializer.save(client=self.request.user.client)