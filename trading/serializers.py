from rest_framework import serializers
from .models import TradingAccount, Trade, PerformanceMetrics, DailyMetrics, AssetPosition

class TradingAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingAccount
        fields = ['id', 'account_name', 'account_id', 'alpaca_api_key', 'alpaca_secret_key', 'is_paper_trading', 'is_active', 'last_sync', 'created_at']
        read_only_fields = ['id', 'last_sync', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TradeSerializer(serializers.ModelSerializer):
    total_value = serializers.ReadOnlyField()

    class Meta:
        model = Trade
        fields = [
            'id', 'trade_id', 'symbol', 'side', 'quantity', 'price', 'filled_price',
            'commission', 'profit_loss', 'status', 'strategy', 'notes', 'timestamp',
            'total_value', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'trade_id', 'total_value', 'created_at', 'updated_at']


class TradeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = [
            'symbol', 'side', 'quantity', 'price', 'commission', 'strategy', 'notes', 'timestamp'
        ]

    def create(self, validated_data):
        # Generate a simple trade_id if not provided
        import uuid
        validated_data['trade_id'] = str(uuid.uuid4())
        return super().create(validated_data)


class PerformanceMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceMetrics
        fields = [
            'total_trades', 'winning_trades', 'losing_trades', 'total_pnl',
            'total_commission', 'largest_win', 'largest_loss', 'average_win',
            'average_loss', 'win_rate', 'profit_factor', 'sharpe_ratio',
            'max_drawdown', 'updated_at'
        ]


class DailyMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyMetrics
        fields = [
            'date', 'portfolio_value', 'daily_pnl', 'trades_count', 'volume', 'created_at'
        ]


class AssetPositionSerializer(serializers.ModelSerializer):
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = AssetPosition
        fields = [
            'symbol', 'quantity', 'average_cost', 'current_price', 'market_value',
            'unrealized_pnl', 'percentage', 'updated_at'
        ]

    def get_percentage(self, obj):
        # Calculate percentage of total portfolio
        total_value = sum(pos.market_value or 0 for pos in obj.account.positions.all())
        if total_value > 0 and obj.market_value:
            return float((obj.market_value / total_value) * 100)
        return 0.0


class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    account_id = serializers.IntegerField()

    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("File must be a CSV file.")
        return value


class LiveMetricsSerializer(serializers.Serializer):
    """Serializer for real-time account metrics"""
    account_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    buying_power = serializers.DecimalField(max_digits=15, decimal_places=2)
    day_trade_count = serializers.IntegerField()
    portfolio_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    last_equity = serializers.DecimalField(max_digits=15, decimal_places=2)
    equity = serializers.DecimalField(max_digits=15, decimal_places=2)
    initial_margin = serializers.DecimalField(max_digits=15, decimal_places=2)
    maintenance_margin = serializers.DecimalField(max_digits=15, decimal_places=2)
    sma = serializers.DecimalField(max_digits=15, decimal_places=2)
    status = serializers.CharField()
