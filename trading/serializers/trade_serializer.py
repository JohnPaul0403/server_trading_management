from . import serializers, TradingAccount, Trade
from decimal import Decimal

class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = [
            'id', 'account', 'symbol', 'side', 'quantity', 'price',
            'commission', 'status', 'strategy', 'notes',
            'timestamp', 'created_at', 'updated_at' 
        ]
        read_only_fields = ['id', 'account', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)