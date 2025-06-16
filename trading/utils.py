from decimal import Decimal
from django.utils import timezone
from .models import PerformanceMetrics, DailyMetrics
import pandas as pd
import numpy as np


class PerformanceCalculator:
    """Calculate trading performance metrics"""

    def __init__(self, trading_account):
        self.account = trading_account

    def update_metrics(self):
        """Update all performance metrics for the account"""
        trades = self.account.trades.filter(status='filled')

        if not trades.exists():
            return self._create_empty_metrics()

        # Calculate basic metrics
        total_trades = trades.count()
        winning_trades = trades.filter(profit_loss__gt=0).count()
        losing_trades = trades.filter(profit_loss__lt=0).count()

        # P&L calculations
        total_pnl = sum(trade.profit_loss or Decimal('0') for trade in trades)
        total_commission = sum(trade.commission for trade in trades)

        # Win/Loss statistics
        wins = [trade.profit_loss for trade in trades if trade.profit_loss and trade.profit_loss > 0]
        losses = [trade.profit_loss for trade in trades if trade.profit_loss and trade.profit_loss < 0]

        largest_win = max(wins) if wins else Decimal('0')
        largest_loss = min(losses) if losses else Decimal('0')
        average_win = sum(wins) / len(wins) if wins else Decimal('0')
        average_loss = sum(losses) / len(losses) if losses else Decimal('0')

        # Win rate
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else Decimal('0')

        # Profit factor
        total_wins = sum(wins) if wins else Decimal('0')
        total_losses = abs(sum(losses)) if losses else Decimal('0')
        profit_factor = (total_wins / total_losses) if total_losses > 0 else Decimal('0')

        # Update or create performance metrics
        performance, created = PerformanceMetrics.objects.get_or_create(
            account=self.account,
            defaults={
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'total_pnl': total_pnl,
                'total_commission': total_commission,
                'largest_win': largest_win,
                'largest_loss': largest_loss,
                'average_win': average_win,
                'average_loss': average_loss,
                'win_rate': win_rate,
                'profit_factor': profit_factor,
            }
        )

        if not created:
            # Update existing metrics
            performance.total_trades = total_trades
            performance.winning_trades = winning_trades
            performance.losing_trades = losing_trades
            performance.total_pnl = total_pnl
            performance.total_commission = total_commission
            performance.largest_win = largest_win
            performance.largest_loss = largest_loss
            performance.average_win = average_win
            performance.average_loss = average_loss
            performance.win_rate = win_rate
            performance.profit_factor = profit_factor
            performance.save()

        # Update daily metrics
        self._update_daily_metrics()

        return performance

    def _create_empty_metrics(self):
        """Create empty performance metrics"""
        performance, created = PerformanceMetrics.objects.get_or_create(
            account=self.account,
            defaults={
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_pnl': Decimal('0'),
                'total_commission': Decimal('0'),
                'largest_win': Decimal('0'),
                'largest_loss': Decimal('0'),
                'average_win': Decimal('0'),
                'average_loss': Decimal('0'),
                'win_rate': Decimal('0'),
                'profit_factor': Decimal('0'),
            }
        )
        return performance

    def _update_daily_metrics(self):
        """Update daily performance metrics"""
        trades = self.account.trades.filter(status='filled').order_by('timestamp')

        if not trades.exists():
            return

        # Group trades by date
        daily_data = {}
        running_pnl = Decimal('0')

        for trade in trades:
            date = trade.timestamp.date()
            if date not in daily_data:
                daily_data[date] = {
                    'trades_count': 0,
                    'daily_pnl': Decimal('0'),
                    'volume': Decimal('0')
                }

            daily_data[date]['trades_count'] += 1
            daily_data[date]['daily_pnl'] += trade.profit_loss or Decimal('0')
            daily_data[date]['volume'] += trade.total_value
            running_pnl += trade.profit_loss or Decimal('0')

        # Create or update daily metrics
        base_portfolio_value = Decimal('100000')  # Starting portfolio value

        for date, data in daily_data.items():
            portfolio_value = base_portfolio_value + running_pnl

            DailyMetrics.objects.update_or_create(
                account=self.account,
                date=date,
                defaults={
                    'portfolio_value': portfolio_value,
                    'daily_pnl': data['daily_pnl'],
                    'trades_count': data['trades_count'],
                    'volume': data['volume']
                }
            )

    def calculate_sharpe_ratio(self, risk_free_rate=0.02):
        """Calculate Sharpe ratio"""
        daily_metrics = DailyMetrics.objects.filter(account=self.account).order_by('date')

        if daily_metrics.count() < 2:
            return None

        # Calculate daily returns
        returns = []
        prev_value = None

        for metric in daily_metrics:
            if prev_value is not None:
                daily_return = float((metric.portfolio_value - prev_value) / prev_value)
                returns.append(daily_return)
            prev_value = metric.portfolio_value

        if not returns:
            return None

        # Calculate Sharpe ratio
        returns_array = np.array(returns)
        excess_returns = returns_array - (risk_free_rate / 252)  # Daily risk-free rate

        if np.std(excess_returns) == 0:
            return None

        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        return Decimal(str(round(sharpe_ratio, 4)))

    def calculate_max_drawdown(self):
        """Calculate maximum drawdown"""
        daily_metrics = DailyMetrics.objects.filter(account=self.account).order_by('date')

        if daily_metrics.count() < 2:
            return Decimal('0')

        values = [float(metric.portfolio_value) for metric in daily_metrics]
        peak = values[0]
        max_drawdown = 0

        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return Decimal(str(round(max_drawdown, 4)))


def calculate_profit_loss(trades_queryset):
    """Calculate P&L for a queryset of trades"""
    buy_trades = {}
    total_pnl = Decimal('0')

    for trade in trades_queryset.order_by('timestamp'):
        symbol = trade.symbol

        if trade.side == 'buy':
            if symbol not in buy_trades:
                buy_trades[symbol] = []
            buy_trades[symbol].append({
                'quantity': trade.quantity,
                'price': trade.filled_price or trade.price,
                'commission': trade.commission
            })

        elif trade.side == 'sell' and symbol in buy_trades:
            remaining_quantity = trade.quantity
            trade_pnl = Decimal('0')

            while remaining_quantity > 0 and buy_trades[symbol]:
                buy_trade = buy_trades[symbol][0]

                if buy_trade['quantity'] <= remaining_quantity:
                    # Use entire buy trade
                    quantity_used = buy_trade['quantity']
                    buy_trades[symbol].pop(0)
                else:
                    # Partial use of buy trade
                    quantity_used = remaining_quantity
                    buy_trades[symbol][0]['quantity'] -= quantity_used

                # Calculate P&L for this portion
                sell_value = quantity_used * (trade.filled_price or trade.price)
                buy_value = quantity_used * buy_trade['price']
                portion_pnl = sell_value - buy_value - trade.commission - buy_trade['commission']

                trade_pnl += portion_pnl
                remaining_quantity -= quantity_used

            # Update trade P&L
            trade.profit_loss = trade_pnl
            trade.save()
            total_pnl += trade_pnl

    return total_pnl
