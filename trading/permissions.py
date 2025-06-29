from rest_framework.permissions import BasePermission
from .models import TradingAccount, Trade

class IsAccountOwner(BasePermission):
    """
    Custom permission to only allow owners of the trading account (or related trade)
    to access or modify it.
    """

    def has_object_permission(self, request, view, obj):
        # For direct account access (TradingAccount instance)
        if isinstance(obj, TradingAccount):
            return obj.user == request.user

        # For trade access, ensure the related account belongs to the user
        if isinstance(obj, Trade):
            return obj.account.user == request.user

        return False
