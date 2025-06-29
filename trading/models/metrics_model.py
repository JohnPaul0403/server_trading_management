from . import models

class SymbolPosition(models.Model):
    account_metrics = models.ForeignKey(
        'AccountMetrics',
        on_delete=models.CASCADE,
        related_name='symbol_positions'
    )
    symbol = models.CharField(max_length=20)

    buy_qty = models.DecimalField(max_digits=20, decimal_places=6)
    sell_qty = models.DecimalField(max_digits=20, decimal_places=6)
    position = models.DecimalField(max_digits=20, decimal_places=6)
    avg_buy_price = models.DecimalField(max_digits=20, decimal_places=4)
    avg_sell_price = models.DecimalField(max_digits=20, decimal_places=4)
    open_position = models.BooleanField()

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('account_metrics', 'symbol')

    def __str__(self):
        return f"{self.symbol} position in account {self.account_metrics.account_id}"


class AccountMetrics(models.Model):
    account = models.OneToOneField(
        'TradingAccount',
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    total_trades = models.IntegerField()
    total_buy_qty = models.DecimalField(max_digits=20, decimal_places=6)
    total_sell_qty = models.DecimalField(max_digits=20, decimal_places=6)
    total_buy_cost = models.DecimalField(max_digits=20, decimal_places=2)
    total_sell_revenue = models.DecimalField(max_digits=20, decimal_places=2)
    net_profit_loss = models.DecimalField(max_digits=20, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
    symbols_traded = models.JSONField(default=list)

    def __str__(self):
        return f"Metrics for account {self.account_id}"