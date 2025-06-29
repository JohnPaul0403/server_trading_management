from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import TradingAccount, Trade, AccountMetrics, SymbolPosition
from ..serializers import (
    TradingAccountSerializer,
    AccountMetricsSerializer,
    AccountDailyPerformanceSerializer,
    OpenAssetSerializer,
    UserMetricsSerializer,
    UserDailyPerformanceSerializer,
    UserOpenAssetSerializer,
    TradeSerializer
)
from ..services import (
    calculate_metrics,
    PerformanceCalculator,
    GetPrices,
    GetOpenAssets,
    import_trades_from_dataframe,
)
from ..permissions import IsAccountOwner

from .trading_account_view import TradingAccountViewSet
from .trade_view import TradeViewSet
from .user_metrics_view import UserDailyPerformanceView, UserOpenAssetsView

__all__ = [
    "TradingAccountViewSet",
    "TradeViewSet",
    "UserDailyPerformanceView",
    "UserOpenAssetsView",
]