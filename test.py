import pandas as pd
import ccxt
import ta 


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
    data['sma20']   = ta.trend.sma_indicator(data['close'], window=20)
    data['sma50']   = ta.trend.sma_indicator(data['close'], window=50)
    data['rsi']     = ta.momentum.RSIIndicator(data['close']).rsi()
    data['macd']    = ta.trend.MACD(data['close']).macd()
    return data

# Determines whether or not the bot will buy at this timestep
def buy_trigger(t, P):
    #TODO fill this
    should_buy = False
    return should_buy

def sell_trigger(t, P):
    #TODO fill this
    should_sell = False

    return should_sell


# Define the bot function
def bot(P):
    data = getOHLCVdata()
    data = setIndicators(data)

    # Initialise holdings
    AUD = 100.0     # starting AUD holdings
    BTC = 0.0       # starting BTC holdings
    buy_triggered = False

    for t in range(len(data)):
        if buy_trigger(t, P) and not buy_triggered:
            buy_triggered = True
            BTC = AUD * (0.98)
            AUD = 0.0
        elif sell_trigger(t, P) and buy_triggered:
            buy_triggered = False
            AUD = BTC  * (0.98)
            BTC = 0.0
        elif t == len(data)-1 and BTC > 0:
            AUD = BTC * (0.98)
            BTC = 0.0

    return AUD


data = getOHLCVdata()
print(setIndicators(data))

exchange = ccxt.kraken()

order_book = exchange.fetch_order_book('BTC/AUD')

print(order_book) 