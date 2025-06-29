from django.db.models import Sum, F, Q
from collections import defaultdict

def calculate_metrics(account):
    trades = account.trades.all()

    total_trades = trades.count()
    total_buy_qty = trades.filter(side='BUY').aggregate(total=Sum('quantity'))['total'] or 0
    total_sell_qty = trades.filter(side='SELL').aggregate(total=Sum('quantity'))['total'] or 0

    total_buy_cost = trades.filter(side='BUY').aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0

    total_sell_revenue = trades.filter(side='SELL').aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0

    net_pl = total_sell_revenue - total_buy_cost

    # Symbols traded
    symbols = trades.values_list('symbol', flat=True).distinct()

    # Position per symbol
    symbol_positions = defaultdict(lambda: {'buy_qty': 0, 'sell_qty': 0, 'avg_buy_price': 0, 'avg_sell_price': 0})

    for symbol in symbols:
        symbol_trades = trades.filter(symbol=symbol)

        buy_trades = symbol_trades.filter(side='BUY')
        sell_trades = symbol_trades.filter(side='SELL')

        buy_qty = buy_trades.aggregate(total=Sum('quantity'))['total'] or 0
        sell_qty = sell_trades.aggregate(total=Sum('quantity'))['total'] or 0

        buy_value = buy_trades.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
        sell_value = sell_trades.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0

        avg_buy_price = (buy_value / buy_qty) if buy_qty else 0
        avg_sell_price = (sell_value / sell_qty) if sell_qty else 0

        position = buy_qty - sell_qty  # this is the open quantity
        open_position = position > 0

        symbol_positions[symbol] = {
            'buy_qty': buy_qty,
            'sell_qty': sell_qty,
            'position': position,
            'avg_buy_price': avg_buy_price,
            'avg_sell_price': avg_sell_price,
            'open_position': open_position,
        }

    print(set(list(symbols)))

    return {
        'total_trades': total_trades,
        'total_buy_qty': total_buy_qty,
        'total_sell_qty': total_sell_qty,
        'total_buy_cost': total_buy_cost,
        'total_sell_revenue': total_sell_revenue,
        'net_profit_loss': net_pl,
        'symbols_traded': set(list(symbols)),
        'symbol_positions': dict(symbol_positions)
    }
