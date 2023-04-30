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
                lit = a[0] > a[1] and a[2] < a[3] and a[0]>0
            elif (P[i][0] == "bb"):
                pass
            elif (P[i][0] == "rsi"):
                a = self.rsi_indicator(t, P[i])
                lit = a.item() < RSI_OVERSOLD
            elif (P[i][0] == "obv"):
                pass
            
            if (i == 0): # for the first literal
                dnf = lit
            elif(P[i][1]==1): # it is an OR conditional
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
                lit = a[0] < a[1] and a[2] > a[3] and a[0] < 0
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
        
        macd_line      = self.data["macd"].loc[t]
        signal_line    = self.data["macd_sig"].loc[t]

        if t-1 > 0:
            prev_macd   = self.data["macd"].loc[t-1]
            prev_signal = self.data["macd_sig"].loc[t-1]
        else:
            prev_macd   = self.data["macd"].loc[0] 
            prev_signal = self.data["macd_sig"].loc[0]
        
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

        # Get close prices for RSI
        if t-1 > 0:
            rsi_line  = self.data["rsi"].loc[t]
        else:
            rsi_line  = self.data["rsi"].loc[0]
        return rsi_line 

    def sma_indicator(self,t,P):
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
        prices = self.data['close']
        for p in self.P:
            type = p[0]
            if type =="macd":
                macd_indicator = ta.trend.MACD(close=prices, window_slow=p[2], window_fast=p[3], window_sign=p[4])
                self.data["macd"] = macd_indicator.macd()
                self.data["macd_sig"] = macd_indicator.macd_signal()
            elif type == "rsi":
                rsi_indicator = ta.momentum.RSIIndicator(close = prices, window = p[2])
                self.data["rsi"] = rsi_indicator.rsi()



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
                print("aud{}".format(AUD))
            # Sell remaining BTC at the end of the test period
            elif t == len(self.data)-1 and BTC > 0:
                AUD = BTC * 0.98 * self.data['close'][t]
                BTC = 0.0
        return AUD
    
    

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
a = TradingBot([["macd", 1, 26, 12, 9]], data)
aud = a.run()
print(aud)