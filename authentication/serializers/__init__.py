from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from ..models import User

user = get_user_model()

from .user_registration_serializer import UserRegistrationSerializer
from .user_login_serializer import UserLoginSerializer
from .user_profile_serializer import UserProfileSerializer, VerifyUserProfileSerializer
from .password_reset_serializer import ForgotPasswordSerializer, ResetPasswordSerializer
from .password_change_serializer import ChangePasswordSerializer

__all__ = [
    "UserRegistrationSerializer",
    "UserLoginSerializer",
    "UserProfileSerializer",
    "VerifyUserProfileSerializer",
    "ForgotPasswordSerializer",
    "ResetPasswordSerializer",
    "ChangePasswordSerializer",
]