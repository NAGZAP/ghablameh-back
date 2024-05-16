from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *





class WalletViewSet(GenericViewSet):
    
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    
    @action(methods=['get'], detail=False)
    def me(self, request):
        wallet = Wallet.objects.get(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)