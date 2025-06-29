from . import serializers
from ..models import SymbolPosition, AccountMetrics

class UserMetricsSerializer(serializers.Serializer):
    total_accounts = serializers.IntegerField()
    total_trades = serializers.IntegerField()
    total_starting_capital = serializers.FloatField()
    total_realized_pl = serializers.FloatField()
    total_current_balance = serializers.FloatField()
    cumulative_return_percent = serializers.FloatField()

class SymbolPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolPosition
        fields = [
            'symbol',
            'buy_qty',
            'sell_qty',
            'position',
            'avg_buy_price',
            'avg_sell_price',
            'open_position',
            'last_updated'
        ]

class AccountMetricsSerializer(serializers.ModelSerializer):
    symbol_positions = SymbolPositionSerializer(many=True, read_only=True)

    class Meta:
        model = AccountMetrics
        fields = [
            'account',
            'total_trades',
            'total_buy_qty',
            'total_sell_qty',
            'total_buy_cost',
            'total_sell_revenue',
            'net_profit_loss',
            'last_updated',
            'symbols_traded',
            'symbol_positions'
        ]
