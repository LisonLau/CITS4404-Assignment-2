import pandas as pd
import ccxt
import ta 

START_WINDOW_FAST = 26
START_WINDOW_SLOW = 12
START_WINDOW_SIGN = 9

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

def setIndicators(data):
    # Calculate some TA indicators using the ta library
    #data['sma20']   = ta.trend.sma_indicator(data['close'], window=20)
    #data['sma50']   = ta.trend.sma_indicator(data['close'], window=50)
    data['rsi']     = ta.momentum.RSIIndicator(data['close']).rsi()
    data['macd']    = ta.trend.MACD(data['close'], START_WINDOW_SLOW, START_WINDOW_FAST, START_WINDOW_SIGN, fillna=True).macd()
    data['macd_signal'] = ta.trend.MACD(data['close'], START_WINDOW_SLOW, START_WINDOW_FAST, START_WINDOW_SIGN, fillna=True).macd_signal()
    data['macd_histogram'] = ta.trend.MACD(data['close'], START_WINDOW_SLOW, START_WINDOW_FAST, START_WINDOW_SIGN, fillna=True).macd_diff()

    return data

# Determines whether or not the bot will buy at this timestep
def buy_trigger(t):
    should_buy = False
    if data['macd'][t] > data['macd_signal'][t] and data['macd'][t-1] <= data['signal'][t-1]:
        should_buy = True
    return should_buy

# Determines whether or not the bot will sell at this timestep
def sell_trigger(t):
    should_sell = False

    if data['macd'][t] < data['macd_signal'][t] and data['macd'][t-1] >= data['signal'][t-1]:
        should_sell = True

    return should_sell


# Define the bot function
#def bot(P):

def bot():
    data = getOHLCVdata()
    data = setIndicators(data)

    # Initialise holdings
    AUD = 100.0     # starting AUD holdings
    BTC = 0.0       # starting BTC holdings
    buy_triggered = False

    for t in range(len(data)):
        if buy_trigger(t) and not buy_triggered:
            buy_triggered = True
            AUD_buy = AUD * 0.98
            BTC = AUD_buy / data['close']
            AUD = 0.0
            print("Current holdings: {} BTC".format(BTC))
        elif sell_trigger(t) and buy_triggered:
            buy_triggered = False
            BTC_sell = BTC * 0.98
            AUD = BTC_sell * data['close']
            BTC = 0.0
            print("Current holdings: ${} AUD".format(AUD))
        elif t == len(data)-1 and BTC > 0:
            BTC_sell = BTC * 0.98
            AUD = BTC_sell * data['close']
            BTC = 0.0

    return AUD


data = getOHLCVdata()
indicator_data = setIndicators(data)
total_earn = bot()

print("Total earnings: {}".format(total_earn))