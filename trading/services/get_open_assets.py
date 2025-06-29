from collections import defaultdict, deque
from .get_prices import GetPrices
from decimal import Decimal

class GetOpenAssets:
    def __init__(self, user, account):
        self.user = user
        self.account = account

    def get(self):
        return self.get_open_assets(self.account)
    
    def get_all(self):
        return self.get_user_open_assets(self.user)

    def get_open_assets(self, account):
        trades = account.trades.order_by('timestamp', 'id')
        buy_queues = defaultdict(deque)  # {symbol: deque of {qty, price}}

        for trade in trades:
            symbol = trade.symbol
            qty = trade.quantity
            price = trade.price
            side = trade.side

            if side == 'BUY':
                buy_queues[symbol].append({'qty': qty, 'price': price})

            elif side == 'SELL':
                remaining_qty = qty
                while remaining_qty > 0 and buy_queues[symbol]:
                    buy_lot = buy_queues[symbol][0]
                    match_qty = min(remaining_qty, buy_lot['qty'])

                    buy_lot['qty'] -= match_qty
                    remaining_qty -= match_qty

                    if buy_lot['qty'] == 0:
                        buy_queues[symbol].popleft()

        # At the end, anything left in the buy_queues is open position
        open_assets = []

        for symbol, queue in buy_queues.items():
            total_qty = 0
            total_cost = Decimal('0.0')

            for lot in queue:
                total_qty += lot['qty']
                total_cost += lot['qty'] * lot['price']

            if total_qty > 0:
                avg_price = total_cost / total_qty if total_qty else 0
                last_price = GetPrices(symbol).get_last_price()
                if last_price is not None:
                    last_price = Decimal(str(last_price))
                else:
                    last_price = Decimal('0.0')
                open_assets.append({
                    'symbol': symbol,
                    'quantity': round(total_qty, 4),
                    'avg_buy_price': round(avg_price, 4),
                    'total_cost': round(total_cost, 2),  # <-- Added comma here
                    'current_price': last_price,
                    'unrealized_pl': round((last_price - avg_price) * total_qty, 2) if last_price else None
                })

        return open_assets
    
    def get_user_open_assets(self, user):
        aggregated = defaultdict(lambda: {'total_qty': Decimal('0.0'), 'total_cost': Decimal('0.0')})

        for account in user.trading_accounts.all():
            open_assets = self.get_open_assets(account)

            for asset in open_assets:
                symbol = asset['symbol']
                qty = asset['quantity']
                cost = asset['total_cost']

                aggregated[symbol]['total_qty'] += qty
                aggregated[symbol]['total_cost'] += cost

        result = []
        for symbol, data in aggregated.items():
            qty = data['total_qty']
            cost = data['total_cost']
            avg_price = cost / qty if qty else 0
            last_price = GetPrices(symbol).get_last_price()

            print(last_price)

            if last_price is not None:
                last_price = Decimal(str(last_price))
            else:
                last_price = Decimal('0.0')

            result.append({
                'symbol': symbol,
                'total_quantity': round(qty, 4),
                'avg_buy_price': round(avg_price, 4),
                'total_cost': round(cost, 2),
                'current_price': round(last_price, 4) if last_price else None,
                'unrealized_pl': round((last_price - avg_price) * qty, 2) if last_price else None
            })

        return result