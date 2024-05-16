from rest_framework import serializers
from .models import Wallet



class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ['user', 'balance', 'created_at', 'updated_at']
        