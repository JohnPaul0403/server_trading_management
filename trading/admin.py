from django.contrib import admin
from .models import TradingAccount, Trade, AccountMetrics, SymbolPosition
# Register your models here.

admin.site.register(TradingAccount)
admin.site.register(Trade)
admin.site.register(AccountMetrics)
admin.site.register(SymbolPosition)