from collections import defaultdict, deque
from datetime import date
from decimal import Decimal

class PerformanceCalculator:
    def __init__(self, user, account):
        self.user = user
        self.account = account

    def calculate(self):
        return self.calculate_daily_performance(self.account)
    
    def calculate_metrics(self):
        return self.get_user_daily_metrics(self.user)

    def calculate_daily_performance(self, account):
        trades = account.trades.order_by('timestamp', 'id')

        buy_queues = defaultdict(deque)  # FIFO queue of (price, quantity) per symbol
        daily_performance = []
        current_balance = account.initial_balance
        prev_day_value = account.initial_balance

        trades_by_day = defaultdict(list)
        for trade in trades:
            trades_by_day[trade.timestamp.date()].append(trade)

        print(trades_by_day.keys())

        all_days = sorted(trades_by_day.keys())

        for day in all_days:
            realized_pl = 0
            day_trades = trades_by_day[day]

            for trade in day_trades:
                symbol = trade.symbol
                qty = trade.quantity
                price = trade.price
                side = trade.side

                if side == 'BUY':
                    buy_queues[symbol].append({'qty': qty, 'price': price})

                elif side == 'SELL':
                    remaining_qty = qty
                    matched_qty = 0
                    pl = 0

                    while remaining_qty > 0 and buy_queues[symbol]:
                        buy_lot = buy_queues[symbol][0]
                        match_qty = min(remaining_qty, buy_lot['qty'])
                        cost_price = buy_lot['price']

                        pl += (price - cost_price) * match_qty

                        buy_lot['qty'] -= match_qty
                        remaining_qty -= match_qty
                        matched_qty += match_qty

                        if buy_lot['qty'] == 0:
                            buy_queues[symbol].popleft()

                    # If not fully matched, discard the trade (open position part ignored)
                    if matched_qty < qty:
                        pl = 0  # Ignore partial P&L
                    else:
                        current_balance += price * matched_qty  # Add revenue

                    realized_pl += pl

            ending_balance = current_balance + realized_pl
            daily_return = (ending_balance - prev_day_value) / prev_day_value if prev_day_value else 0
            cumulative_return = (ending_balance - account.initial_balance) / account.initial_balance

            daily_performance.append({
                'date': day,
                'starting_balance': prev_day_value,
                'realized_pl': round(realized_pl, 2),
                'ending_balance': round(ending_balance, 2),
                'daily_return': round(daily_return * 100, 2),
                'cumulative_return': round(cumulative_return * 100, 2),
            })

            prev_day_value = ending_balance
            current_balance = ending_balance

        return daily_performance
    
    def get_user_daily_metrics(self, user):
        all_daily = defaultdict(lambda: {
            'starting_balance': Decimal('0.0'),
            'realized_pl': Decimal('0.0'),
            'ending_balance': Decimal('0.0'),
            'dates': set()
        })
        total_starting_capital = Decimal('0.0')

        for account in user.trading_accounts.all():
            daily = self.calculate_daily_performance(account)
            if not daily:
                continue
            total_starting_capital += daily[0]['starting_balance']

            for entry in daily:
                date_key = entry['date']
                all_daily[date_key]['starting_balance'] += entry['starting_balance']
                all_daily[date_key]['realized_pl'] += entry['realized_pl']
                all_daily[date_key]['ending_balance'] += entry['ending_balance']
                all_daily[date_key]['dates'].add(account.id)

        # Sort and compute daily + cumulative return
        sorted_days = sorted(all_daily.items(), key=lambda x: x[0])
        result = []
        prev_day_value = total_starting_capital

        for date_key, data in sorted_days:
            ending = data['ending_balance']
            daily_return = (ending - prev_day_value) / prev_day_value if prev_day_value else 0
            cumulative_return = (ending - total_starting_capital) / total_starting_capital if total_starting_capital else 0

            result.append({
                'date': date_key,
                'starting_balance': round(data['starting_balance'], 2),
                'realized_pl': round(data['realized_pl'], 2),
                'ending_balance': round(ending, 2),
                'daily_return': round(daily_return * 100, 2),
                'cumulative_return': round(cumulative_return * 100, 2)
            })

            prev_day_value = ending

        return result

