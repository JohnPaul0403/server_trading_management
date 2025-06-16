from django.contrib import admin
from .models import TradingAccount, Trade, PerformanceMetrics, DailyMetrics, AssetPosition
# Register your models here.

admin.site.register(TradingAccount)
admin.site.register(Trade)
admin.site.register(PerformanceMetrics)
admin.site.register(DailyMetrics)
admin.site.register(AssetPosition)
