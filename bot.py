import pandas as pd
import ccxt
import ta
import random

RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
class TradingBot:
    # Constructor for TradingBot
    def __init__(self, parameters, data):
        # P format = [window_slow, window_fast, window_sign]
        self.P = parameters
        # self.window_fast = parameters[0]
        # self.window_slow = parameters[1]
        # self.window_sign = parameters[2]
        self.data = data
        # Initialize any other necessary attributes
    
    # Buy trigger function
    def buy_trigger(self, t, P):
        return self.buy(t, P) and not self.buy(t-1, P) and not (self.sell(t, P) and not self.sell(t-1, P))

    # Sell trigger function
    def sell_trigger(self, t, P):
        return self.sell(t, P) and not self.sell(t-1, P) and not (self.buy(t, P) and not self.buy(t-1, P))

    # Buy function
    def buy(self, t, P):
        dnf = 1
        for i in range(len(P)):
            lit = 1
            if (P[i][0] == "macd"):
                a = self.macd_indicator(t,P[i])
                lit = a[0] > a[1] and a[2] < a[3]
            elif (P[i][0] == "bb"):
                pass
            elif (P[i][0] == "rsi"):
                a = self.rsi_indicator(t, P[i])
                lit = a.item() < RSI_OVERSOLD
            elif (P[i][0] == "obv"):
                pass
            
            if (i == 0): # for the first literal
                dnf = lit
            elif(P[i][1]): # it is an OR conditional
                dnf = dnf or lit 
            else: # it is an AND conditional
                dnf = dnf and lit
        return dnf
    
    # Sell function
    def sell(self, t, P):
        dnf = 1
        for i in range(len(P)):
            if (P[i][0] == "macd"):
                a = self.macd_indicator(t,P[i])
                lit = a[0] < a[1] and a[2] > a[3]
                print(lit)
            elif (P[i][0] == "bb"):
                a = self.bb_indicator(t, P[i])
                pass
            elif (P[i][0] == "rsi"):
                a = self.rsi_indicator(t, P[i])

                lit = a.item() > RSI_OVERBOUGHT
            elif (P[i][0] == "obv"):
                pass

            if (i == 0): # for the first literal
                dnf = lit
            elif(P[i][1]): # it is an OR conditional
                dnf = dnf or lit 
            else:
                dnf = dnf and lit
        return dnf

    def macd_indicator(self, t, P):
        # Define MACD parameters from P
        w_slow = int(P[2])
        w_fast = int(P[3])
        w_sign = int(P[4])
        
        # Get close prices data for MACD calculation
        prices = self.data.loc[:t, 'close']
        macd_indicator = ta.trend.MACD(close=prices, window_slow=w_slow, window_fast=w_fast, window_sign=w_sign)
        macd_line      = macd_indicator.macd().loc[t]
        signal_line    = macd_indicator.macd_signal().loc[t]

        if t-1 > 0:
            prev_macd   = macd_indicator.macd().loc[t-1] 
            prev_signal = macd_indicator.macd_signal().loc[t-1]
        else:
            prev_macd   = macd_indicator.macd().loc[0] 
            prev_signal = macd_indicator.macd_signal().loc[0]
        
        return [macd_line, signal_line, prev_macd, prev_signal]


    def bb_indicator(self,t,P):
        # Define Bollinger Bands parameters
        window = int(P[2])
        window_dev = int(P[3])

        prices = self.data.loc[:t, 'close']
        bb_ind = ta.volatility.BollingerBands(close=prices,
                                              window=window,
                                              window_dev=window_dev)


    def rsi_indicator(self,t,P):
        # Define RSI parameters from P
        rsi_window = int(P[2])

        # Get close prices for RSI
        prices = self.data.loc[:t, 'close']

        rsi_indicator = ta.momentum.RSIIndicator(close = prices, window = rsi_window)

        if t-1 > 0:
            rsi_line  = rsi_indicator.rsi().loc[t-1] 
        else:
            rsi_line  = rsi_indicator.rsi().loc[0] 

        return rsi_line 

    def obv_indicator(self,t,P):
        pass

    # if need make for o,h,l,c,v data
    def candle_value(self,t):
        pass

    # Run the trading bot
    def run(self):
        # Initialise variables
        AUD = 100.0     # starting AUD holdings
        BTC = 0.0       # starting BTC holdings
        buy_triggered = False
        
        # Loop through each day in the data
        for t in range(len(self.data)):
            # Check if a buy trigger occurs and there is no concurrent sell trigger
            if self.buy_trigger(t, self.P) and not buy_triggered:
                buy_triggered = True
                BTC = AUD * 0.98 / self.data['close'][t]
                AUD = 0.0
            # Check if a sell trigger occurs and there is no concurrent buy trigger
            elif self.sell_trigger(t, self.P) and buy_triggered:
                buy_triggered = False
                AUD = BTC * 0.98 * self.data['close'][t]
                BTC = 0.0
            # Sell remaining BTC at the end of the test period
            elif t == len(self.data)-1 and BTC > 0:
                AUD = BTC * 0.98 * self.data['close'][t]
                BTC = 0.0
        return AUD
    
    
"""
# Define the buy function using MACD indicator
# TODO: this is definitely not correct :D
def buy(t, P, data):
    # Define MACD parameters from P
    w_slow = int(P[0])
    w_fast = int(P[1])
    w_sign = int(P[2])
    
    # Get close prices data for MACD calculation
    prices = data.loc[:t, 'close']
    
    # Calculate MACD and signal lines for t
    macd_indicator = ta.trend.MACD(close=prices, window_slow=w_slow, window_fast=w_fast, window_sign=w_sign, fillna= True)
    macd_line      = macd_indicator.macd().loc[t]
    signal_line    = macd_indicator.macd_signal().loc[t]
    if t-1 >= 0:
        prev_macd   = macd_indicator.macd().loc[0] 
        prev_signal = macd_indicator.macd_signal().loc[0]
    else:
        prev_macd   = macd_indicator.macd().loc[0] 
        prev_signal = macd_indicator.macd_signal().loc[0]
    # Trigger buy signal if MACD line is above signal line
    return (macd_line > signal_line) and (prev_macd <= prev_signal)

# Define the sell function using MACD indicator
# TODO: this is definitely not correct :D
def sell(t, P, data):
    # Define MACD parameters from P
    w_slow = int(P[0])
    w_fast = int(P[1])
    w_sign = int(P[2])
    
    # Get close prices data for MACD calculation
    prices = data.loc[:t, 'close']
    
    # Calculate MACD and signal lines for t
    macd_indicator = ta.trend.MACD(close=prices, window_slow=w_slow, window_fast=w_fast, window_sign=w_sign, fillna= True)
    macd_line      = macd_indicator.macd().loc[t]
    signal_line    = macd_indicator.macd_signal().loc[t]
    if t-1 >= 0:
        prev_macd   = macd_indicator.macd().loc[0] 
        prev_signal = macd_indicator.macd_signal().loc[0]
    else:
        prev_macd   = macd_indicator.macd().loc[0] 
        prev_signal = macd_indicator.macd_signal().loc[0]
    # Trigger sell signal if MACD line is below signal line
    return (macd_line < signal_line) and (prev_macd >= prev_signal)
"""

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

data = getOHLCVdata()
# data['rsi'] = ta.momentum.RSIIndicator(data['close']).rsi()
# data['macd'] = ta.trend.MACD(data['close']).macd()
# data['macd_signal'] = ta.trend.MACD(data['close']).macd_signal()
# print(data[10:70])
# a = TradingBot([["macd", 1, 26, 12, 9]],data)
a = TradingBot([["rsi", 1, 14]], data)
aud = a.run()
print(aud)