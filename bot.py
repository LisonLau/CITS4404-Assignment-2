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

"""def setIndicators(data):
    # Calculate some TA indicators using the ta library
    #data['sma20']   = ta.trend.sma_indicator(data['close'], window=20)
    #data['sma50']   = ta.trend.sma_indicator(data['close'], window=50)
    data['rsi']     = ta.momentum.RSIIndicator(data['close']).rsi()
    data['macd']    = ta.trend.MACD(data['close'], START_WINDOW_SLOW, START_WINDOW_FAST, START_WINDOW_SIGN, fillna=True).macd()
    data['macd_signal'] = ta.trend.MACD(data['close'], START_WINDOW_SLOW, START_WINDOW_FAST, START_WINDOW_SIGN, fillna=True).macd_signal()
    data['macd_histogram'] = ta.trend.MACD(data['close'], START_WINDOW_SLOW, START_WINDOW_FAST, START_WINDOW_SIGN, fillna=True).macd_diff()

    return data
"""

# Determines whether or not the bot will buy at this timestep
def buy_trigger(t, P, data):
    should_buy = False

    window_slow = P[0]
    window_fast = P[1]
    window_sign = P[2] 
    rsi_window = P[3]

    # Get close prices of past few timestamps for MACD calculation
    prices = data['close'][:t]

    macd_ind = ta.trend.MACD(close=prices, window_slow=window_slow,
                         window_fast = window_fast, window_sign=window_sign)
    macd = macd_ind.macd().loc[t]
    macd_signal = macd_ind.signal().loc[t]
    prev_macd = macd_ind.macd().loc[t-1]
    prev_signal = macd_ind.signal().loc[t-1]

    rsi_ind = ta.trend.RSI(close=prices, window=rsi_window)
    rsi_current = rsi_ind.loc[t]
    
    if (macd > macd_signal and prev_macd > prev_signal) or rsi_current <= RSI_OVERSOLD:
        should_buy = True

    return should_buy

# Determines whether or not the bot will sell at this timestep
def sell_trigger(t):
    should_sell = False

    if data['macd'][t] < data['macd_signal'][t] and data['macd'][t-1] >= data['macd_signal'][t-1]:
        should_sell = True

    return should_sell


# Define the bot function
#def bot(P):

def trade_bot():
    data = getOHLCVdata()

    # Initialise holdings
    AUD = 100.0     # starting AUD holdings
    BTC = 0.0       # starting BTC holdings
    buy_triggered = False

    for t in range(len(data)):
        if buy_trigger(t) and not buy_triggered:
            print("Buying on {}".format(data['timestamp'][t]))
            buy_triggered = True
            AUD_buy = AUD * 0.98
            BTC = AUD_buy / data['close'][t]
            AUD = 0.0
            print("Current holdings: {} BTC".format(BTC))
        elif sell_trigger(t) and buy_triggered:
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


data = getOHLCVdata()
total_earn = trade_bot()