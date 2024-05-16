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
            if user.is_verified:
                return Response({"code":successCode
                            ,"tokens":get_tokens(user)
                             })
            else:
                return Response({"code":successCode
                            ,"message":"email not verified"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"code":successCode
                            ,"message":"username or password not correct"},status=status.HTTP_400_BAD_REQUEST)
        
        
        
class VerificationViewSet(GenericViewSet):
    
    def get_serializer_class(self):
        if self.action=="verify":
            return EmailVerificationSerializer
        elif self.action=="resend":
            return ResendEmailVerificationSerializer

        
    @action(['POST'],False)
    def verify(self,request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # verify the user email
        user = User.objects.get(email=serializer.validated_data['email'])
        user.is_verified = True
        user.save()
        return Response({"message":"ایمیل تایید شد"})
    
    
    @action(['POST'],False)
    def resend(self,request):
        serializer = ResendEmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data['email'])
        verification = EmailVerification.objects.get(user=user)
        try:
            verification.send_verification_email()
        except Exception as e:
            return Response({"message":"خطا در ارسال ایمیل"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message":"ایمیل تایید مجددا ارسال شد"})
    
    
    
        
