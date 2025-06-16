import pandas as pd
import random
from datetime import datetime, timedelta
import csv

# Configuration
symbols = ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'MSFT', 'META', 'GOOG']
sides = ['buy', 'sell']
strategies = ['momentum', 'mean_reversion', 'breakout', 'scalping', 'swing', 'day_trading', '']
notes_options = [
    'Good entry point',
    'Stop loss triggered',
    'Profit target hit',
    'Market volatility',
    'News catalyst',
    'Technical breakout',
    'Support level',
    'Resistance level',
    '',
    ''  # Empty notes more common
]

# Stock price ranges (approximate realistic prices)
price_ranges = {
    'AAPL': (150, 200),
    'TSLA': (180, 280),
    'NVDA': (400, 800),
    'AMZN': (120, 180),
    'MSFT': (350, 450),
    'META': (300, 500),
    'GOOG': (2500, 2800)
}

def generate_random_timestamp(start_date, end_date):
    """Generate random timestamp between two dates"""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Random number of seconds between start and end
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    
    # Add random time within the day
    random_time = start + timedelta(seconds=random_seconds)
    
    # Add random hours, minutes, seconds, microseconds for more realistic timestamps
    random_time = random_time.replace(
        hour=random.randint(9, 16),  # Trading hours
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=random.randint(0, 999999)
    )
    
    # Format as ISO string with Z suffix
    return random_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def generate_random_price(symbol):
    """Generate random price for a symbol within realistic range"""
    min_price, max_price = price_ranges[symbol]
    price = random.uniform(min_price, max_price)
    return round(price, 2)

def generate_random_commission():
    """Generate random commission (0-10 dollars)"""
    return round(random.uniform(0, 10), 2)

def generate_trades_csv(num_trades=1000, filename='random_trades.csv'):
    """Generate CSV file with random trades - creates pairs of opposite trades"""
    
    trades = []
    
    # Generate pairs of trades (buy/sell for same symbol)
    # If num_trades is odd, we'll generate one extra trade to make pairs
    pairs_to_generate = num_trades // 2
    
    for _ in range(pairs_to_generate):
        symbol = random.choice(symbols)
        quantity = random.randint(100, 200)
        strategy = random.choice(strategies)
        
        # Generate buy price and sell price (sell should be different from buy)
        buy_price = generate_random_price(symbol)
        # Sell price can be higher (profit) or lower (loss) than buy price
        price_change_percent = random.uniform(-0.15, 0.20)  # -15% to +20% change
        sell_price = round(buy_price * (1 + price_change_percent), 2)
        
        # Generate timestamps - sell should come after buy
        buy_timestamp = generate_random_timestamp('2025-05-15', '2025-06-15')
        
        # Convert to datetime to add time for sell order
        buy_dt = datetime.strptime(buy_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
        # Sell happens 1 minute to 7 days later
        sell_delay_seconds = random.randint(60, 7 * 24 * 60 * 60)  # 1 min to 7 days
        sell_dt = buy_dt + timedelta(seconds=sell_delay_seconds)
        
        # Make sure sell doesn't exceed end date
        end_date = datetime.strptime('2025-06-15', '%Y-%m-%d')
        if sell_dt > end_date:
            sell_dt = end_date - timedelta(hours=random.randint(1, 24))
        
        sell_timestamp = sell_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        # Create buy trade
        buy_trade = {
            'symbol': symbol,
            'side': 'buy',
            'quantity': quantity,
            'price': buy_price,
            'timestamp': buy_timestamp,
            'commission': generate_random_commission(),
            'strategy': strategy,
            'notes': random.choice(notes_options)
        }
        
        # Create corresponding sell trade
        sell_trade = {
            'symbol': symbol,
            'side': 'sell',
            'quantity': quantity,  # Same quantity
            'price': sell_price,
            'timestamp': sell_timestamp,
            'commission': generate_random_commission(),
            'strategy': strategy,  # Same strategy
            'notes': random.choice(notes_options)
        }
        
        trades.extend([buy_trade, sell_trade])
    
    # If original num_trades was odd, add one more random trade
    if num_trades % 2 == 1:
        symbol = random.choice(symbols)
        single_trade = {
            'symbol': symbol,
            'side': random.choice(sides),
            'quantity': random.randint(100, 200),
            'price': generate_random_price(symbol),
            'timestamp': generate_random_timestamp('2025-05-15', '2025-06-15'),
            'commission': generate_random_commission(),
            'strategy': random.choice(strategies),
            'notes': random.choice(notes_options)
        }
        trades.append(single_trade)
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(trades)
    
    # Sort by timestamp for more realistic data
    df['timestamp_sort'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp_sort').drop('timestamp_sort', axis=1)
    
    # Save to CSV
    df.to_csv(filename, index=False)
    
    print(f"Generated {len(trades)} trades ({pairs_to_generate} pairs) and saved to {filename}")
    print(f"Date range: 2025-05-15 to 2025-06-15")
    print(f"Symbols: {symbols}")
    print(f"Quantity range: 100-200")
    print("Note: Each buy trade has a corresponding sell trade for the same symbol")
    print("\nFirst 10 rows (showing trade pairs):")
    print(df.head(10))
    
    return df

# Generate the CSV file
if __name__ == "__main__":
    trades_df = generate_trades_csv(1000, 'random_trades_1000_2.csv')
    
    # Show some statistics
    print(f"\nDataset Statistics:")
    print(f"Total trades: {len(trades_df)}")
    print(f"Symbols distribution:")
    print(trades_df['symbol'].value_counts())
    print(f"\nSides distribution:")
    print(trades_df['side'].value_counts())
    print(f"\nPrice range by symbol:")
    print(trades_df.groupby('symbol')['price'].agg(['min', 'max', 'mean']).round(2))