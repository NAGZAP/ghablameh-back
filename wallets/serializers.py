from rest_framework import serializers
from .models import Wallet



class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ['user', 'balance', 'created_at', 'updated_at']
        
        
        
class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=11, decimal_places=0)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
    
    
class VerifySerializer(serializers.Serializer):
    token = serializers.CharField()
    
    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Token is required")
        return value