from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderStatus, QueryOrderStatus
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from .models import Trade, AssetPosition
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AlpacaService:
    """Service for Alpaca API integration using alpaca-py"""

    def __init__(self, trading_account):
        self.account = trading_account

        # Validate that account has API credentials
        if not trading_account.alpaca_api_key or not trading_account.alpaca_secret_key:
            raise ValueError("Trading account must have Alpaca API credentials configured")

        # Initialize trading client using account's credentials
        self.trading_client = TradingClient(
            api_key=trading_account.alpaca_api_key,
            secret_key=trading_account.alpaca_secret_key,
            paper=trading_account.is_paper_trading  # Use account's paper trading setting
        )

        # Initialize data client for historical data using account's credentials
        self.data_client = StockHistoricalDataClient(
            api_key=trading_account.alpaca_api_key,
            secret_key=trading_account.alpaca_secret_key
        )

    def get_account_info(self):
        """Get account information from Alpaca"""
        try:
            account = self.trading_client.get_account()
            return {
                'account_value': Decimal(str(account.portfolio_value)),
                'buying_power': Decimal(str(account.buying_power)),
                'day_trade_count': account.daytrade_count,
                'portfolio_value': Decimal(str(account.portfolio_value)),
                'last_equity': Decimal(str(account.last_equity)),
                'equity': Decimal(str(account.equity)),
                'initial_margin': Decimal(str(account.initial_margin)),
                'maintenance_margin': Decimal(str(account.maintenance_margin)),
                'sma': Decimal(str(account.sma)),
                'status': account.status
            }
        except Exception as e:
            logger.error(f"Error fetching account info for account {self.account.account_id}: {e}")
            raise

    def sync_trades(self, days_back=30):
        """Sync trades from Alpaca API"""
        try:
            # Calculate the after timestamp
            after_date = timezone.now() - timedelta(days=days_back)

            # Create the request for filled orders
            request = GetOrdersRequest(
                status=QueryOrderStatus.CLOSED,
                limit=500,
                after=after_date
            )

            # Get orders from the last N days
            orders = self.trading_client.get_orders(filter=request)

            trades_synced = 0
            for order in orders:
                if order.legs:
                    for leg in order.legs:
                        # Check if trade already exists
                        if Trade.objects.filter(trade_id=str(leg.id)).exists():
                            continue

                        # Get filled price - prioritize filled_avg_price, then limit_price
                        filled_price = None
                        if leg.filled_avg_price:
                            filled_price = Decimal(str(leg.filled_avg_price))

                        price = Decimal(str(leg.limit_price or leg.filled_avg_price or 0))

                        # Create trade record
                        trade = Trade.objects.create(
                            account=self.account,
                            trade_id=str(leg.id),
                            symbol=leg.symbol,
                            side=leg.side.value,  # Convert enum to string
                            quantity=Decimal(str(leg.qty)) if leg.qty else 0,
                            price=price,
                            filled_price=filled_price,
                            status='filled',
                            timestamp=leg.filled_at or leg.created_at
                        )
                        trades_synced += 1
                        logger.info(f"Synced trade: {trade}")

                    continue

                # Check if trade already exists
                if Trade.objects.filter(trade_id=str(order.id)).exists():
                    continue

                # Get filled price - prioritize filled_avg_price, then limit_price
                filled_price = None
                if order.filled_avg_price:
                    filled_price = Decimal(str(order.filled_avg_price))

                price = Decimal(str(order.limit_price or order.filled_avg_price or 0))

                # Create trade record
                trade = Trade.objects.create(
                    account=self.account,
                    trade_id=str(order.id),
                    symbol=order.symbol,
                    side=order.side.value,  # Convert enum to string
                    quantity=Decimal(str(order.qty)) if order.qty else 0,
                    price=price,
                    filled_price=filled_price,
                    status='filled',
                    timestamp=order.filled_at or order.created_at
                )
                trades_synced += 1
                logger.info(f"Synced trade: {trade}")

            # Update last sync time
            self.account.last_sync = timezone.now()
            self.account.save()

            return trades_synced

        except Exception as e:
            logger.error(f"Error syncing trades for account {self.account.account_id}: {e}")
            raise

    def get_positions(self):
        """Get current positions from Alpaca"""
        try:
            positions = self.trading_client.get_all_positions()

            # Clear existing positions
            AssetPosition.objects.filter(account=self.account).delete()

            # Create new position records
            for position in positions:
                # Handle optional fields that might be None
                current_price = None
                if position.current_price:
                    current_price = Decimal(str(position.current_price))

                market_value = None
                if position.market_value:
                    market_value = Decimal(str(position.market_value))

                unrealized_pnl = None
                if position.unrealized_pl:
                    unrealized_pnl = Decimal(str(position.unrealized_pl))

                AssetPosition.objects.create(
                    account=self.account,
                    symbol=position.symbol,
                    quantity=Decimal(str(position.qty)),
                    average_cost=Decimal(str(position.avg_entry_price)),
                    current_price=current_price,
                    market_value=market_value,
                    unrealized_pnl=unrealized_pnl
                )

            return len(positions)

        except Exception as e:
            logger.error(f"Error fetching positions for account {self.account.account_id}: {e}")
            raise

    def get_portfolio_history(self, period='1M'):
        """Get portfolio history from Alpaca"""
        try:
            # Convert period string to appropriate parameters
            period_map = {
                '1D': {'period': '1D', 'timeframe': '1Min'},
                '1W': {'period': '1W', 'timeframe': '5Min'},
                '1M': {'period': '1M', 'timeframe': '1Hour'},
                '3M': {'period': '3M', 'timeframe': '1Day'},
                '1Y': {'period': '1Y', 'timeframe': '1Day'},
                'ALL': {'period': 'all', 'timeframe': '1Day'}
            }

            params = period_map.get(period, period_map['1M'])

            history = self.trading_client.get_portfolio_history(
                period=params['period'],
                timeframe=params['timeframe']
            )

            return {
                'timestamps': history.timestamp,
                'equity': history.equity,
                'profit_loss': history.profit_loss,
                'profit_loss_pct': history.profit_loss_pct
            }
        except Exception as e:
            logger.error(f"Error fetching portfolio history for account {self.account.account_id}: {e}")
            raise

    def get_market_data(self, symbol, timeframe='1Day', limit=100):
        """Get market data for a symbol (new functionality)"""
        try:
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day if timeframe == '1Day' else TimeFrame.Hour,
                limit=limit
            )

            bars = self.data_client.get_stock_bars(request)
            return bars.df  # Returns pandas DataFrame

        except Exception as e:
            logger.error(f"Error fetching market data for {symbol} for account {self.account.account_id}: {e}")
            raise
