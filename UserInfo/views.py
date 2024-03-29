from ErrorCode import *
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import *
from rest_framework.authtoken.models import Token


@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, world!"})


class UserInfo(GenericViewSet):

    # def get_serializer_class(self):
    #     if self.action=="login":
    #         return LoginSerializer
    #     elif self.action== "signup":
    #         return SignUpSerializer
    

    @action(['POST'] , False)
    def getUser(self,request):
        serializer = GetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = Token.objects.get(key=validated_data["token"]).user
        
        if user:
            return Response({"code":successCode
                            ,"user":user
                             })
        return Response({"code":tokeNotFound
                            ,"message":"token not found sign up again"},status=status.HTTP_400_BAD_REQUEST)
        
        
        
    
    
    @action(['UPDATE'] , False)
    def UpdateUser(self,request):
        serializer = UpdateSerializer(data=request.data)
        #check that this email didn't exist
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user":  UpdateSerializer(user).data,
                "code":  successCode,
                
            },
            status=status.HTTP_202_ACCEPTED)
    


        