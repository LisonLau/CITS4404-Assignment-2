import pandas as pd
import ccxt
import ta
import random

RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

class TradingBot:
    
    # Constructor for TradingBot
    def __init__(self, parameters, data):
        self.P = parameters
        self.data = data
    
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
                a = self.macd_indicator(t)
                lit = a[0] > a[1] and a[2] < a[3] and a[0] > 0
            elif (P[i][0] == "bb"):
                a = self.bb_indicator(t)
                lit = a[0] > self.data['close'][t] and a[2] < self.data['close'][t-1]
            elif (P[i][0] == "rsi"):
                a = self.rsi_indicator(t)
                lit = a.item() < RSI_OVERSOLD
            elif (P[i][0] == "sma"):
                a = self.sma_indicator(t)
                lit = a[0] > self.data['close'][t] and a[1] <= self.data['close'][t-1]
            if (i == 0):            # for the first literal
                dnf = lit
            elif(P[i][1]==1):       # it is an OR conditional
                dnf = dnf or lit 
            else:                   # it is an AND conditional
                dnf = dnf and lit
        return dnf
    
    # Sell function
    def sell(self, t, P):
        dnf = 1
        for i in range(len(P)):
            if (P[i][0] == "macd"):
                a = self.macd_indicator(t)
                lit = a[0] < a[1] and a[2] > a[3] and a[0] < 0
            elif (P[i][0] == "rsi"):
                a = self.rsi_indicator(t)
                lit = a.item() > RSI_OVERBOUGHT   
            elif (P[i][0] == "sma"):
                a = self.sma_indicator(t)
                lit = a[0] < self.data['close'][t] and a[1] >= self.data['close'][t-1] 
            elif (P[i][0] == "bb"):
                a = self.bb_indicator(t)
                lit = a[1] < self.data['close'][t] and a[3] > self.data['close'][t-1]
            if (i == 0):            # for the first literal
                dnf = lit
            elif(P[i][1]):          # it is an OR conditional
                dnf = dnf or lit 
            else:                   # it is an AND conditional
                dnf = dnf and lit
        return dnf

    # MACD indicator
    def macd_indicator(self, t):
        macd_line      = self.data["macd"].loc[t]
        signal_line    = self.data["macd_sig"].loc[t]
        
        if t-1 > 0:
            prev_macd   = self.data["macd"].loc[t-1]
            prev_signal = self.data["macd_sig"].loc[t-1]
        else:
            prev_macd   = self.data["macd"].loc[0] 
            prev_signal = self.data["macd_sig"].loc[0]
        
        return [macd_line, signal_line, prev_macd, prev_signal]

    # RSI indicator
    def rsi_indicator(self, t):
        if t-1 > 0:
            rsi_line  = self.data["rsi"].loc[t]
        else:
            rsi_line  = self.data["rsi"].loc[0]
        return rsi_line 

    # BB indicator    
    def bb_indicator(self, t):
        lower_band = self.data["bb_lower"][t]
        upper_band = self.data["bb_upper"][t]
        
        if t-1 > 0:
            prev_lower = self.data["bb_lower"][t-1]
            prev_upper = self.data["bb_upper"][t-1]
        else:
            prev_lower = self.data["bb_lower"][0]
            prev_upper = self.data["bb_upper"][0]
        return [lower_band, upper_band, prev_lower, prev_upper]

    def sma_indicator(self, t):
        current = self.data["sma"].loc[t]
        if t-1 > 0:
            previous = self.data["sma"].loc[t-1]
        else:
            previous = self.data["sma"].loc[0]
        return [current, previous]

    # If need make for OHLVC data
    def candle_value(self, t):
        pass

    # Run the trading bot
    def run(self):
        # Initialise variables
        AUD = 100.0     # starting AUD holdings
        BTC = 0.0       # starting BTC holdings
        buy_triggered = False
        prices = self.data['close']
        
        # Store indicators in the dataframe
        for p in self.P:
            type = p[0]
            if type =="macd":
                macd_indicator = ta.trend.MACD(close=prices, window_slow=p[2], window_fast=p[3], window_sign=p[4])
                self.data["macd"] = macd_indicator.macd()
                self.data["macd_sig"] = macd_indicator.macd_signal()
            elif type == "rsi":
                rsi_indicator = ta.momentum.RSIIndicator(close=prices, window=p[2])
                self.data["rsi"] = rsi_indicator.rsi()
            elif type == "bb":
                bb_indicator = ta.volatility.BollingerBands(close=prices, window=p[2], window_dev=p[3])
                self.data["bb_lower"] = bb_indicator.bollinger_lband()
                self.data["bb_upper"] = bb_indicator.bollinger_hband()
            elif type == "sma":
                sma_indicator = ta.trend.SMAIndicator(close=prices, window=p[2])
                self.data["sma"] = sma_indicator.sma_indicator()
        
        # Loop through each day in the data
        for t in range(len(self.data)):
            # Check if a buy trigger occurs and there is no concurrent sell trigger
            if self.buy_trigger(t, self.P) and not buy_triggered:
                buy_triggered = True
                BTC = AUD * 0.98 / self.data['close'][t]
                AUD = 0.0
                print("btc {}".format(BTC))
            # Check if a sell trigger occurs and there is no concurrent buy trigger
            elif self.sell_trigger(t, self.P) and buy_triggered:
                buy_triggered = False
                AUD = BTC * 0.98 * self.data['close'][t]
                BTC = 0.0
                print("aud {}".format(AUD))
            # Sell remaining BTC at the end of the test period
            elif t == len(self.data)-1 and BTC > 0:
                AUD = BTC * 0.98 * self.data['close'][t]
                BTC = 0.0
        return AUD
    
    
# def getOHLCVdata():
#     # Initialize the Kraken exchange
#     kraken = ccxt.kraken()
#     # Retrieve the historical data for BTC/AUD from the Kraken exchange
#     ohlcv = kraken.fetch_ohlcv('BTC/AUD', '1d')
#     # Convert the data to a pandas DataFrame
#     data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
#     # Convert the timestamp to a datetime object
#     data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
#     return data

# data = getOHLCVdata()
# a = TradingBot([["bb", 1, 20, 2], ["macd", 1, 26, 12, 9], ["rsi", 1, 14], ["bb", 1, 20, 2]], data)
# aud = a.run()
# print(aud)

# MACD  = ["macd", 1, 26, 12, 9]
# RSI   = ["rsi", 1, 14]
# BB    = ["bb", 1, 20, 2]
# SMA   = ["sma", 1, 20]