from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()

class TradingAccount(models.Model):
    """Trading account model for Alpaca integration"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trading_accounts')
    account_id = models.CharField(max_length=100, unique=True)
    account_name = models.CharField(max_length=100)
    alpaca_api_key = models.CharField(max_length=200, blank=True)
    alpaca_secret_key = models.CharField(max_length=200, blank=True)
    is_paper_trading = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trading_account'

    def __str__(self):
        return f"{self.user.email} - {self.account_name}"

class Trade(models.Model):
    """Individual trade record"""
    SIDE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    STATUS_CHOICES = [
        ('filled', 'Filled'),
        ('partially_filled', 'Partially Filled'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]

    account = models.ForeignKey(TradingAccount, on_delete=models.CASCADE, related_name='trades')
    trade_id = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=10)
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    quantity = models.DecimalField(max_digits=15, decimal_places=6, validators=[MinValueValidator(Decimal('0.000001'))])
    price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    filled_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='filled')
    strategy = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trading_trade'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.symbol} {self.side} {self.quantity} @ {self.price}"

    @property
    def total_value(self):
        """Calculate total trade value"""
        return self.quantity * (self.filled_price or self.price)

class PerformanceMetrics(models.Model):
    """Account performance metrics"""
    account = models.OneToOneField(TradingAccount, on_delete=models.CASCADE, related_name='performance')
    total_trades = models.IntegerField(default=0)
    winning_trades = models.IntegerField(default=0)
    losing_trades = models.IntegerField(default=0)
    total_pnl = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_commission = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    largest_win = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    largest_loss = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    average_win = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    average_loss = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    profit_factor = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.0000'))
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.0000'))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trading_performancemetrics'

    def __str__(self):
        return f"Performance for {self.account.account_name}"


class DailyMetrics(models.Model):
    """Daily performance tracking"""
    account = models.ForeignKey(TradingAccount, on_delete=models.CASCADE, related_name='daily_metrics')
    date = models.DateField()
    portfolio_value = models.DecimalField(max_digits=15, decimal_places=2)
    daily_pnl = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    trades_count = models.IntegerField(default=0)
    volume = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'trading_dailymetrics'
        unique_together = ['account', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.account.account_name} - {self.date}"


class AssetPosition(models.Model):
    """Current asset positions"""
    account = models.ForeignKey(TradingAccount, on_delete=models.CASCADE, related_name='positions')
    symbol = models.CharField(max_length=10)
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    average_cost = models.DecimalField(max_digits=15, decimal_places=2)
    current_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    market_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    unrealized_pnl = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trading_assetposition'
        unique_together = ['account', 'symbol']

    def __str__(self):
        return f"{self.account.account_name} - {self.symbol}: {self.quantity}"
