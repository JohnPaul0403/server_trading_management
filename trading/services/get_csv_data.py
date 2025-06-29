from . import Trade
import pandas as pd
from django.utils import timezone

def import_trades_from_dataframe(csv_file, account):
    if not csv_file:
        return {"message": "No file uploaded."}
    
    df = pd.read_csv(csv_file, parse_dates=['timestamp'])
    df.dropna(subset=['symbol', 'price', 'quantity', 'side', 'timestamp'], inplace=True)
    
    if df.empty:
        return {"message": "No valid trades found."}
    
    # standardize
    df['side'] = df['side'].str.lower()
    df['symbol'] = df['symbol'].str.upper()
    
    # ensure timestamp aware
    df['timestamp'] = df['timestamp'].apply(
        lambda ts: timezone.make_aware(ts) if timezone.is_naive(ts) else ts
    )

    # generate trade_ids if missing
    if 'trade_id' not in df.columns or df['trade_id'].isnull().any():
        df['trade_id'] = [
            f'csv_{account.id}_{sym}_{ts.isoformat()}'
            for sym, ts in zip(df['symbol'], df['timestamp'])
        ]
    
    # create the Trade objects efficiently
    trades_to_create = [
        Trade(
            account=account,
            symbol=row['symbol'],
            side=row['side'],
            quantity=row['quantity'],
            price=row['price'],
            timestamp=row['timestamp'],
            commission=row.get('commission', 0) or 0,
            status=row.get('status', 'filled') if 'status' in row else 'filled',
            strategy=row.get('strategy', ''),
            notes=row.get('notes', '')
        )
        for row in df.to_dict('records')
    ]

    # bulk create
    Trade.objects.bulk_create(trades_to_create, batch_size=500)

    return {
        "message": f"{len(trades_to_create)} trades imported successfully."
    }

