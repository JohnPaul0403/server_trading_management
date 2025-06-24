from . import serializers, User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail

class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for requesting email verification.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """
        Validate email format without revealing if user exists.
        """
        try:
            user = User.objects.get(email=value)
            if not user.is_active:
                # Don't reveal account status for security
                pass
        except User.DoesNotExist:
            # Don't reveal whether email exists or not for security
            # But we'll still validate the format
            pass
        return value

    def save(self):
        """
        Generate verification token and send email if user exists.
        """
        email = self.validated_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Generate token and uid
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create verification URL
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"
            
            # Send email
            subject = 'Email Verification - Trading Dashboard'
            message = render_to_string('email_verification.html', {
                'user': user,
                'verification_url': verification_url,
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
        
        return {'message': 'If the email exists, a verification link has been sent.'}


class EmailVerificationConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming email verification via token.
    """
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        Validate the verification token and uid.
        """
        try:
            uid = urlsafe_base64_decode(attrs['uid']).decode()
            user = User.objects.get(pk=uid, is_active=True)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid verification link.")

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Invalid or expired verification token.")

        attrs['user'] = user
        return attrs

    def save(self):
        """
        Mark email as verified.
        """
        user = self.validated_data['user']
        
        # Mark email as verified using your custom User model
        user.is_verified = True
        user.save(update_fields=['is_verified', 'updated_at'])
        
        return {
            'message': 'Email verified successfully.',
            'user_id': user.id,
            'email': user.email
        }