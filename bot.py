import pandas as pd
import ccxt
import ta 

PARAMETER_RANGES = {
    "window_slow": range(20, 60),
    "window_fast": range(10, 20),
    "window_slow": range(10, 20),
    "rsi_window": range(10, 30)
}

RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

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

def trigger(t, P, data, buy_triggered):
    buyStr = 'BUY'
    sellStr = 'SELL'

    window_slow = P[0]
    window_fast = P[1]
    window_sign = P[2] 
    
    prices = data.loc[:t, 'close']

    macd_ind = ta.trend.MACD(close=prices, window_slow=window_slow,
                         window_fast = window_fast, window_sign=window_sign, fillna=True)
    macd = macd_ind.macd().loc[t]
    macd_signal = macd_ind.macd_signal().loc[t]

    if t-1 > 0:
        prev_macd = macd_ind.macd().loc[t-1]
        prev_signal = macd_ind.macd_signal().loc[t-1]
    else:
        prev_macd = macd_ind.macd().loc[0]
        prev_signal = macd_ind.macd_signal().loc[0]

    if (macd < macd_signal and prev_macd >= prev_signal) and buy_triggered is True:
        return sellStr
    
    elif (macd > macd_signal and prev_macd <= prev_signal) and buy_triggered is False:
        return buyStr


# Define bot function
def trade_bot(P):
    data = getOHLCVdata()

    # Initialise holdings
    AUD = 100.0     # starting AUD holdings
    BTC = 0.0       # starting BTC holdings
    buy_triggered = False

    for t in range(len(data)):
        if trigger(t, P, data, buy_triggered) == "BUY":
            print("Buying on {}".format(data['timestamp'][t]))
            buy_triggered = True
            AUD_buy = AUD * 0.98
            BTC = AUD_buy / data['close'][t]
            AUD = 0.0
            print("Current holdings: {} BTC".format(BTC))
        elif trigger(t, P, data, buy_triggered) == "SELL":
            print("Selling on {}".format(data['timestamp'][t]))
            buy_triggered = False
            BTC_sell = BTC * 0.98
            AUD = BTC_sell * data['close'][t]
            BTC = 0.0
            print("Current holdings: ${} AUD".format(AUD))
        elif t == len(data)-1 and BTC > 0.0:
            BTC_sell = BTC * 0.98
            AUD = BTC_sell * data['close'][t]
            BTC = 0.0
            print("Total earnings: ${} AUD".format(AUD))

    return AUD

P = [26, 12, 9, 14]
data = getOHLCVdata()
total_earn = trade_bot(P)