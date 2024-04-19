from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from rest_framework.decorators import action 
from .permissions import *
from .tokens import get_tokens
from .models import (Organization,Client,Buffet)
from food_reservation.clients.serializers import *
from food_reservation.organizations.serializers import *
from .serializers import *
from ErrorCode import *



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
    
    def get_permissions(self):
        if self.action in ['me', 'password']:
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



class BuffetViewSet(ModelViewSet):

    serializer_class = BuffetSerializer

    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            return [IsClient()]
        else:
            return [IsClient(),IsOrganizationAdmin()]
        
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
        
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    
        
        
    



    
