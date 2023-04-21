import ccxt
import ta
import pandas as pd

# Retrieve OHLCV data
def getOHLCVdata():
    # Initialize the Kraken exchange
    kraken = ccxt.kraken()
    # Retrieve the historical data for BTC/AUD from the Kraken exchange
    ohlcv = kraken.fetch_ohlcv('BTC/AUD', '1d')
    # Convert the data to a pandas DataFrame
    data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    # Convert the timestamp to a datetime object
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    return data

# Calculate MACD indicator using the ta library
def calculateMACD(data):
    data['macd'] = ta.trend.MACD(data['close']).macd()
    return data

def buy_trigger(t, P, data):
    # get MACD values for previous and current days
    macd_prev = ta.trend.MACD(data['close'][t-1], window_slow=P[0], window_fast=P[1], window_sign=P[2]).macd_signal()[t-2]
    macd_curr = ta.trend.MACD(data['close'][t], window_slow=P[0], window_fast=P[1], window_sign=P[2]).macd_signal()[t-1]
    # get signal values for previous and current days
    signal_prev = ta.trend.MACD(data['close'][t-1], window_slow=P[0], window_fast=P[1], window_sign=P[2]).macd()[t-2]
    signal_curr = ta.trend.MACD(data['close'][t], window_slow=P[0], window_fast=P[1], window_sign=P[2]).macd()[t-1]
    # generate buy signal if MACD crosses above signal and both are positive
    return (macd_prev < signal_prev and macd_curr > signal_curr and macd_curr > 0 and signal_curr > 0)

def sell_trigger(t, P, data):
    # get MACD values for previous and current days
    macd_prev = ta.trend.MACD(data['close'][t-1], window_slow=P[0], window_fast=P[1], window_sign=P[2]).macd_signal()[t-2]
    macd_curr = ta.trend.MACD(data['close'][t], window_slow=P[0], window_fast=P[1], window_sign=P[2]).macd_signal()[t-1]
    # get signal values for previous and current days
    signal_prev = ta.trend.MACD(data['close'][t-1], window_slow=P[0], window_fast=P[1], window_sign=P[2]).macd()[t-2]
    signal_curr = ta.trend.MACD(data['close'][t], window_slow=P[0], window_fast=P[1], window_sign=P[2]).macd()[t-1]
    # generate sell signal if MACD crosses below signal and both are negative
    return (macd_prev > signal_prev and macd_curr < signal_curr and macd_curr < 0 and signal_curr < 0)

# Define the bot function
# P format = (window_slow, window_fast, window_sign)
def bot(P):
    data = getOHLCVdata()
    data = calculateMACD(data)
    
    # Initialise holdings
    AUD = 100.0     # starting AUD holdings
    BTC = 0.0       # starting BTC holdings
    buy_triggered = False

    for t in range(len(data)):
        if buy_trigger(t, P, data) and not buy_triggered:
            buy_triggered = True
            BTC = AUD * (0.98)
            AUD = 0.0
        elif sell_trigger(t, P, data) and buy_triggered:
            buy_triggered = False
            AUD = BTC  * (0.98)
            BTC = 0.0
        elif t == len(data)-1 and BTC > 0:
            AUD = BTC * (0.98)
            BTC = 0.0
    return AUD





