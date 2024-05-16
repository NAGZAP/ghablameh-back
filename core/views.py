from ErrorCode import *
import logging
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import ForgetPasswordVerification
from .tokens import get_tokens
from .serializers import *

logger = logging.getLogger(__name__)

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
        if self.action=="verify_email":
            return EmailVerificationSerializer
        elif self.action=="resend":
            return ResendEmailVerificationSerializer
        elif self.action=="forget_password":
            return ForgetPasswordSerializer
        elif self.action=="forget_password_verify":
            return ForgetPasswordVerificationSerializer
        

        
    @action(['POST'],False)
    def verify_email(self,request):
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
    
    
    @action(['POST'],False)
    def forget_password(self,request):
        # TODO: make security better
        serializer = ForgetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data['email'])
        (verification,created) = ForgetPasswordVerification.objects.get_or_create(user=user)
        try:
            verification.send_verification_email()
        except Exception as e:
            logger.error(str(e))
            return Response({"message":"خطا در ارسال ایمیل"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message":"ایمیل تایید فراموشی رمز عبور ارسال شد"})
    
    @action(['POST'],False)
    def forget_password_verify(self,request):
        serializer = ForgetPasswordVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"رمز عبور تغییر یافت"})    
        
