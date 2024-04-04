from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from rest_framework.decorators import action 
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .permissions import *
from .tokens import get_tokens
from .models import (Organization,Client,Buffet)
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
        if action == 'login':
            return OrganizationLoginSerializer
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
        

    
    @action(['POST'] , False)
    def login(self,request):
        serializer = OrganizationLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = authenticate(username=validated_data["username"],password=validated_data["password"])
        if user and hasattr(user, 'organization_admin'):
            return Response( { "tokens":get_tokens(user)})
        elif user:
            return Response( {"message":"امکان لاگین به عنوان ادمین سازمان وجود ندارد" },status=status.HTTP_403_FORBIDDEN)
        return Response( {"message":"نام کاربری یا رمز عبور اشتباه است" },status=status.HTTP_400_BAD_REQUEST)
        
        
        
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
        if action == 'login':
            return ClientLoginSerializer
        if action == 'me':
            if self.request.method == 'GET':
                return ClientSerializer           
            return ClientUpdateSerializer
        if action == 'password':
            return ClientChangePasswordSerializer
    
    def get_permissions(self):
        if self.action in ['me', 'password']:
            return [IsAuthenticated(),IsNotOrganizationAdmin()]
        else:
            return []
    
    @action(['POST'] , False)
    def login(self,requset):
        serializer = ClientLoginSerializer(data=requset.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = authenticate(username=validated_data["username"],password=validated_data["password"])
        if user:
            return Response( { "tokens":get_tokens(user)})
        return Response( {"message":"نام کاربری یا رمز عبور اشتباه است" },status=status.HTTP_400_BAD_REQUEST)
        
        
    

    @action(['POST'] , False)
    def register(self,requset):

        serializer = ClientRegisterSerializer(data=requset.data)
        serializer.is_valid(raise_exception=True)
        client = serializer.save()
        
        return Response({
            "client":ClientSerializer(client).data,
            'tokens' : get_tokens(client.user),
        },status=status.HTTP_201_CREATED)
    



    @action(['GET','PUT'] , False)
    def me(self,request):

        instance = request.user.client

        if request.method == 'PUT':
            serializer = ClientUpdateSerializer(instance,data=request.data)
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



class BuffetViewSet(ModelViewSet):

    serializer_class = BuffetSerializer

    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated(),IsOrganizationAdmin()]
        

    def get_queryset(self):

        org = self.request.user.organization_admin.organization
        if hasattr(self.request.user,'organizaion_admin'):
            return Buffet.objects.filter(organization=org).all()

    
        

    
        
        
    



    
