from . import serializers, validate_password

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        """
        Validate that the old password is correct.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        """
        Validate the new password using Django's password validators.
        """
        user = self.context['request'].user
        validate_password(value, user)
        return value

    def validate(self, attrs):
        """
        Validate that new password and confirm password match.
        """
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords do not match.")
        
        # Check that new password is different from old password
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError("New password cannot be the same as old password.")
        
        return attrs

    def save(self, **kwargs):
        """
        Update the user's password.
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user