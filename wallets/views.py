import logging
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Wallet, Payment
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from . import paygate

logger = logging.getLogger(__name__)



class WalletViewSet(GenericViewSet):
    
    def get_serializer_class(self):
        if self.action == 'deposit':
            return DepositSerializer
        elif self.action == 'verify':
            return VerifySerializer
        return WalletSerializer
    
    permission_classes = [IsAuthenticated]
    
    @action(methods=['get'], detail=False)
    def me(self, request):
        wallet = Wallet.objects.get(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)
    
    
    @action(methods=['post'], detail=False)
    def deposit(self, request):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)   
        amount = serializer.validated_data['amount']
        try:
            token = paygate.token(amount)
        except Exception as e:
            logger.error(e)
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        data = {
            'token': token,
            'amount': amount,
            'pgw_url': paygate.URL,
            'pgw_callback_url': paygate.CALL_BACK_URL
        }
        Payment.objects.create(token=token, amount=amount, user=request.user)
        return Response(data)
    
    
    @action(methods=['post'], detail=False)
    def verify(self, request):
        serializer = VerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)   
        token = serializer.validated_data['token']
        amount = Payment.objects.filter(token=token, user=request.user).first().amount
        wallet = Wallet.objects.get(user=request.user)
        if amount is None:
            return Response({'error': 'Token not found or this token is not related to you'}, status=status.HTTP_404_NOT_FOUND)
        try:
            result = paygate.verify(token)
        except Exception as e:
            logger.error(e)
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        if result is None:
            return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)
        if result is False:
            return Response({'error': 'Token is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        wallet.deposit(amount)
        return Response({'status': 'COMPLETED'})

    @action(methods=['post'], detail=False)
    def check_status(self, request):
        serializer = VerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)   
        token = serializer.validated_data['token']
        try:
            result = paygate.check_status(token)
        except Exception as e:
            logger.error(e)
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({'status': 'COMPLETED' if result else 'PENDING'})