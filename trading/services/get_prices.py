import yfinance as yf

class GetPrices:
    """
    A class to fetch historical market data for a given ticker symbol.
    """

    def __init__(self, ticker: str):
        """
        Initialize the GetPrices class with ticker, period, and interval.

        :param ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL').
        :param period: Data period (e.g., '1d', '5d', '1mo', '1y', '5y', 'max').
        :param interval: Data interval (e.g., '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1d').
        """
        self.ticker = ticker

    def get_data(self, period='1y', interval='1d'):
        """
        Fetch historical market data for the initialized ticker symbol.

        :return: Pandas DataFrame with historical market data.
        """
        return get_data(self.ticker, period, interval)
    
    def get_last_price(self):
        """
        Fetch the last available price for the initialized ticker symbol.

        :return: Last price as a float.
        """
        data = self.get_data(period='1d', interval='1m')
        if not data.empty:
            return data['Close'].iloc[-1].iloc[0]
        else:
            return None

def get_data(ticker: str, period: str = '1y', interval: str = '1d'):
    """
    Fetch historical market data for a given ticker symbol.

    :param ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL').
    :param period: Data period (e.g., '1d', '5d', '1mo', '1y', '5y', 'max').
    :param interval: Data interval (e.g., '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1d').
    :return: Pandas DataFrame with historical market data.
    """
    try:
        data = yf.download(ticker, period=period, interval=interval)
        return data
    except Exception as e:
        raise ValueError(f"Error fetching data for {ticker}: {str(e)}")
