from . import serializers

class AccountDailyPerformanceSerializer(serializers.Serializer):
    date = serializers.DateField()
    starting_balance = serializers.FloatField()
    realized_pl = serializers.FloatField()
    ending_balance = serializers.FloatField()
    daily_return = serializers.FloatField()
    cumulative_return = serializers.FloatField()

class UserDailyPerformanceSerializer(serializers.Serializer):
    date = serializers.DateField()
    starting_balance = serializers.FloatField()
    realized_pl = serializers.FloatField()
    ending_balance = serializers.FloatField()
    daily_return = serializers.FloatField()
    cumulative_return = serializers.FloatField()
