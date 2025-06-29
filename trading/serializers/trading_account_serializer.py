from . import serializers, TradingAccount

class TradingAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingAccount
        fields = ['id', 'account_name', 'initial_balance', 'currency', 'is_paper_trading', 'is_active', 'last_sync', 'created_at']
        read_only_fields = ['id', 'last_sync', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)