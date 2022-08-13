import ccxt
import config
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', 15)

import numpy as np

# from datetime import datetime
# import time
# import matplotlib.pyplot as plt

exchange = ccxt.ftx({
    'apiKey': config.FTX_API_KEY,
    'secret': config.FTX_SECRET_KEY
})

bars = exchange.fetch_ohlcv('ETH-PERP', timeframe='1d', limit=1000)
df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')


def tr(dr):
    df['previous_close'] = df['close'].shift(1)
    df['high-low'] = abs(df['high'] - df['low'])
    df['high-pc'] = abs(df['high'] - df['previous_close'])
    df['low-pc'] = abs(df['low'] - df['previous_close'])

    tr = df[['high-low', 'high-pc', 'low-pc']].max(axis=1)

    return tr


def atr(df, period):
    df['tr'] = tr(df)
    atr = df['tr'].rolling(period).mean()

    return atr


# df['atr'] = the_atr
# print(df)

def supertrend(df, period=7, multiplier=3):
    hl2 = (df['high'] + df['low']) / 2

    df['atr'] = atr(df, period)
    df['upperband'] = hl2 + (multiplier * df['atr'])
    df['lowerband'] = hl2 - (multiplier * df['atr'])
    df['in_uptrend'] = True


    for current in range(1, len(df.index)):
        previous = current - 1

        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]

    if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
        df['lowerband'][current] = df['lowerband'][previous]

    if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
        df['upperband'][current] = df['upperband'][previous]

    return df
#print(current)

print(df)

print(supertrend(df))

df['tr'] = tr(df)


# balance = exchange.fetch_balance()
# print(balance['total']['USD'])
# print(balance['total']['BTC'])


# markets = exchange.load_markets()
# ticker = exchange.fetch_ticker('CREAM-PERP')
# print(ticker)

# ohlc = exchange.fetch_ohlcv('CREAM-PERP')
# for candle in ohlc:
#   print(candle)

# btc_ticker = ftx.fetch_ticker('BTC/USDT')

# ftx_btc_usdt_ohlcv = ftx.fetch_ohlcv('BTC/USDT', '1d',limit=100)
