from ErrorCode import *
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .tokens import get_tokens
from .serializers import *

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, world!"})


class Authentication(GenericViewSet):

    def get_serializer_class(self):
        if self.action=="login":
            return LoginSerializer
        elif self.action== "signup":
            return SignUpSerializer
    

    @action(['POST'] , False)
    def login(self,request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = authenticate(username=validated_data["username"],password=validated_data["password"])
        if user:
            return Response({"code":successCode
                            ,"tokens":get_tokens(user)
                             })
        return Response({"code":successCode
                            ,"message":"username or password not correct"},status=status.HTTP_400_BAD_REQUEST)
        
        
        
    
    
    @action(['POST'] , False)
    def signup(self,request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user":  UserSerializer(user).data,
                "code":  successCode,
                "tokens": get_tokens(user),
            },
            status=status.HTTP_201_CREATED)

        