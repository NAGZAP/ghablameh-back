from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from rest_framework.decorators import action, api_view
from .permissions import *
from .tokens import get_tokens
from .models import (Organization,Client,Buffet,Reserve)
from food_reservation.clients.serializers import *
from food_reservation.organizations.serializers import *
from .serializers import *
from ErrorCode import *
from rest_framework.exceptions import NotFound


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
        queryset = request.user.client.organizations.all()
        serializer = OrganizationListSerializer(queryset,many=True)
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
        

    def get_queryset(self):
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

        if not Buffet.objects.filter(
            id=self.kwargs['buffet_pk'],
            organization__in=self.request.user.client.organizations.all()
        ).exists():
            raise NotFound()
        
        return Rate.objects.filter(
            buffet_id=self.kwargs['buffet_pk'], client=self.request.user.client
        ).select_related('client','buffet','client__user')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['buffet_id'] = self.kwargs['buffet_pk']
        context['client_id'] = self.request.user.client.id
        return context
    
    

    def perform_create(self, serializer):
        serializer.save(client=self.request.user.client, buffet_id=self.kwargs['buffet_pk'])

    def perform_update(self, serializer):
        serializer.save(client=self.request.user.client, buffet_id=self.kwargs['buffet_pk'])
