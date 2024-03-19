from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .tokens import get_tokens
from .serializers import LoginSerializer,SignUpSerializer
from ErrorCode import *
from models import User
from rest_framework import generics

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, world!"})

# /auth/
class Authentication(GenericViewSet):

    def get_serializer_class(self):
        if self.action=="login":
            return LoginSerializer
        elif self.action== "signup":
            return SignUpSerializer
    
    # /auth/login
    @action(['POST'] , False)
    def login(self,request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid()
        validated_data = serializer.validated_data
        print(validated_data)
        user = authenticate(username=validated_data["username"],password=validated_data["password"])
        if user:
            return Response({"code":successCode
                            ,"tokens":get_tokens(user)
                             })
        return Response({"code":successCode
                            ,"message":"username or password not correct"},status=status.HTTP_400_BAD_REQUEST)
        
        
        
    
    
    @action(['POST'] , False)
    def signup(self,request):
        queryset = User.objects.all()
        serializer = SignUpSerializer
    
        validated_data = serializer.validated_data
        user = authenticate(username=validated_data["username"],password=validated_data["password"])
        return Response({"code":successCode,"tokens":get_tokens(user)})

        

    # serializer.save()
    
    
    # models -> model -> table -> ORM -> [Model].objects
    # urls routing - request -> function (method) [views] ->
    # views -> models -> response
    # example: /users GET -> view -> Class.list() -> view -> User.objects.all() -> response : incorrect
    # request -> url -> view -> serializer
    # serializer -> Model
    # serializer : 1- type checking, json serialize dict-> json, json -> dict, save, update
    # login save update,check
