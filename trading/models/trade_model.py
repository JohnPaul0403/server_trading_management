from . import models, MinValueValidator, Decimal
from .trading_account_model import TradingAccount

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
    symbol = models.CharField(max_length=10)
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    quantity = models.DecimalField(max_digits=15, decimal_places=6, validators=[MinValueValidator(Decimal('0.000001'))])
    price = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
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