from . import serializers, User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_verified', 'created_at')
        read_only_fields = ('id', 'email', 'is_verified', 'created_at')
