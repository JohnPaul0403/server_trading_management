from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from ..models import User

user = get_user_model()

from .user_registration_serializer import UserRegistrationSerializer
from .user_login_serializer import UserLoginSerializer
from .user_profile_serializer import UserProfileSerializer
from .password_reset_serializer import ForgotPasswordSerializer, ResetPasswordSerializer
from .password_change_serializer import ChangePasswordSerializer
from .email_verification_serializer import EmailVerificationSerializer, EmailVerificationConfirmSerializer

__all__ = [
    "UserRegistrationSerializer",
    "UserLoginSerializer",
    "UserProfileSerializer",
    "ForgotPasswordSerializer",
    "ResetPasswordSerializer",
    "ChangePasswordSerializer",
    "EmailVerificationSerializer",
    "EmailVerificationConfirmSerializer",
]