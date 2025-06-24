from . import serializers, User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
    
class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset via email.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """
        Validate that the email exists in our system.
        """
        try:
            user = User.objects.get(email=value)
            if not user.is_active:
                raise serializers.ValidationError("This account is deactivated.")
        except User.DoesNotExist:
            # Don't reveal whether email exists or not for security
            # But we'll still validate the format
            pass
        return value

    def save(self):
        """
        Generate reset token and send email.
        """
        email = self.validated_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Generate token and uid
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset URL (you'll need to configure this in your frontend)
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            # Send email
            subject = 'Password Reset Request - Trading Dashboard'
            message = render_to_string('password_reset.html', {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'Trading Dashboard',
            })
            
            send_mail(
                subject=subject,
                message='',  # Plain text version
                html_message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
        except User.DoesNotExist:
            # Don't reveal that user doesn't exist
            # But we still process the request silently
            pass
        
        return {'message': 'If the email exists, a reset link has been sent.'}

class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for actually resetting the password with token.
    """
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """
        Validate the reset token and password confirmation.
        """
        try:
            # Decode the user ID
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid reset link.")

        # Check if token is valid
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Invalid or expired reset link.")

        # Check password confirmation
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        # Validate new password
        validate_password(attrs['new_password'], user)

        # Store user for save method
        attrs['user'] = user
        return attrs

    def save(self):
        """
        Reset the user's password.
        """
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        
        # Optional: Send confirmation email
        send_mail(
            subject='Password Successfully Reset - Trading Dashboard',
            message=f'Hello {user.first_name}, your password has been successfully reset.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        
        return user