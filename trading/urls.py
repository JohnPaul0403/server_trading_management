from django.urls import path, include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register(r'accounts', views.TradingAccountViewSet, basename='accounts')

# Nested router for trades under accounts
trades_router = routers.NestedDefaultRouter(router, r'accounts', lookup='account')
trades_router.register(r'trades', views.TradeViewSet, basename='account-trades')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(trades_router.urls)),
    path('user-metrics/', views.UserDailyPerformanceView.as_view(), name='user-metrics'),
    path('user-open-assets/', views.UserOpenAssetsView.as_view(), name='user-open-assets'),
]
