from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'accounts', views.TradingAccountViewSet, basename='tradingaccount')
router.register(r'trades', views.TradeViewSet, basename='trade')

urlpatterns = [
    path('', include(router.urls)),
    path('metrics/<int:account_id>/', views.PerformanceMetricsView.as_view(), name='performance-metrics'),
    path('positions/<int:account_id>/', views.AssetPositionListView.as_view(), name='asset-positions'),
]
