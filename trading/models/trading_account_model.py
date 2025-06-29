from . import User, models, Decimal

class TradingAccount(models.Model):
    """Trading account model for Alpaca integration"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trading_accounts')
    account_name = models.CharField(max_length=100)
    initial_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=10, default='USD')
    is_paper_trading = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trading_account'

    def __str__(self):
        return f"{self.user.email} - {self.account_name}"