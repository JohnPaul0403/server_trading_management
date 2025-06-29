from . import serializers

class OpenAssetSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    quantity = serializers.FloatField()
    avg_buy_price = serializers.FloatField()
    total_cost = serializers.FloatField()
    current_price = serializers.FloatField(allow_null=True)
    unrealized_pl = serializers.FloatField(allow_null=True)

class UserOpenAssetSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    total_quantity = serializers.FloatField()
    avg_buy_price = serializers.FloatField()
    total_cost = serializers.FloatField()
    current_price = serializers.FloatField(allow_null=True)
    unrealized_pl = serializers.FloatField(allow_null=True)