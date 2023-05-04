import ta
import matplotlib.pyplot as plt
import pandas as pd
import ccxt
import header

RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

class TradingBot:
    
    # Constructor for TradingBot
    def __init__(self, parameters, data):
        self.P = parameters
        self.data = data
        self.obv_window = 30
        self.current_buy = 0
        self.prev_buy = 0
        self.current_sell = 0
        self.prev_sell = 0
        self.aud_holdings = []
    
    # Buy trigger function
    def buy_trigger(self, t, P):
        return self.buy(t, P) and not self.prev_buy and not (self.sell(t, P) and not self.prev_sell)

    # Sell trigger function
    def sell_trigger(self, t, P):
        return self.sell(t, P) and not self.prev_sell and not (self.buy(t, P) and not self.prev_buy)

    # Buy function
    def buy(self, t, P):
        dnf = 1
        for i in range(len(P)):
            if (P[i][0] == ""):
                continue
            lit = 0
            if (P[i][0] == "macd"):
                a = self.macd_indicator(t)
                lit = a[0] > a[1] and a[2] < a[3] and a[0] > 0
            elif (P[i][0] == "bb"):
                a = self.bb_indicator(t)
                lit = a[0] > self.data.loc[t, 'close'] and a[2] < self.data.loc[t-1, 'close']
            elif (P[i][0] == "rsi"):
                a = self.rsi_indicator(t)
                lit = a.item() < P[i][3]
            elif (P[i][0] == "sma"):
                a = self.sma_indicator(t)
                lit = a[0] > a[1] and a[2] < a[3]
            elif (P[i][0] == "obv" and t >= 30):
                a = self.obv_indicator(t)
                lit = a[0] < a[1] and self.data.loc[t-30, 'close'] > self.data.loc[t, 'close']
            if (i == 0):            # for the first literal
                dnf = lit
            elif(P[i][1]==1):       # it is an OR conditional
                dnf = dnf or lit 
            else:                   # it is an AND conditional
                dnf = dnf and lit
        self.current_buy = dnf
        return dnf
    
    # Sell function
    def sell(self, t, P):
        dnf = 1
        for i in range(len(P)):
            if (P[i][0] == ""):
                continue
            lit = 0
            if (P[i][0] == "macd"):
                a = self.macd_indicator(t)
                lit = a[0] < a[1] and a[2] > a[3] and a[0] < 0
            elif (P[i][0] == "rsi"):
                a = self.rsi_indicator(t)
                lit = a.item() > P[i][4]
            elif (P[i][0] == "sma"):
                a = self.sma_indicator(t)
                lit = a[0] < a[1] and a[2] > a[3] 
            elif (P[i][0] == "bb"):
                a = self.bb_indicator(t)
                lit = a[1] < self.data.loc[t, 'close'] and a[3] > self.data.loc[t-1, 'close']
            elif (P[i][0] == "obv" and t >= 30):
                a = self.obv_indicator(t)
                lit = a[0] > a[1] and self.data.loc[t-30, 'close']< self.data.loc[t, 'close']
            if (i == 0):            # for the first literal
                dnf = lit
            elif(P[i][1]):          # it is an OR conditional
                dnf = dnf or lit 
            else:                   # it is an AND conditional
                dnf = dnf and lit
        self.current_sell = dnf
        return dnf

    # MACD indicator
    def macd_indicator(self, t):
        macd_line      = self.data.loc[t, 'macd']
        signal_line    = self.data.loc[t, 'macd_sig']
        if t-1 > 0:
            prev_macd   = self.data.loc[t-1, 'macd']
            prev_signal = self.data.loc[t-1, 'macd_sig']
        else:
            prev_macd   = self.data.loc[0, 'macd']
            prev_signal = self.data.loc[0, 'macd_sig']
        return [macd_line, signal_line, prev_macd, prev_signal]

    # RSI indicator
    def rsi_indicator(self, t):
        if t-1 > 0:
            rsi_line  = self.data.loc[t, 'rsi']
        else:
            rsi_line  = self.data.loc[0, 'rsi']
        return rsi_line 

    # BB indicator    
    def bb_indicator(self, t):
        lower_band = self.data.loc[t, 'bb_lower']
        upper_band = self.data.loc[t, 'bb_upper']
        if t-1 > 0:
            prev_lower = self.data.loc[t-1, 'bb_lower']
            prev_upper = self.data.loc[t-1, 'bb_upper']
        else:
            prev_lower = self.data.loc[0, 'bb_lower']
            prev_upper = self.data.loc[0, 'bb_upper']
        return [lower_band, upper_band, prev_lower, prev_upper]

    def sma_indicator(self, t):
        current_low = self.data.loc[t, 'sma_low']
        current_upp = self.data.loc[t, 'sma_upp']
        if t-1 > 0:
            prev_low = self.data.loc[t-1, 'sma_low']
            prev_upp = self.data.loc[t-1, 'sma_upp']
        else:
            prev_low = self.data.loc[0, 'sma_low']
            prev_upp = self.data.loc[0, 'sma_upp']
        return [current_low, current_upp, prev_low, prev_upp]
    
    def obv_indicator(self, t):
        cur_vol = self.data.loc[t, 'obv']
        if t-self.obv_window >= 0:
            prev_vol = self.data.loc[t-self.obv_window, 'obv']
        else:
            prev_vol = self.data.loc[0, 'obv']
        return [cur_vol, prev_vol]

    # If need make for OHLVC data
    def candle_value(self, t):
        pass

    # Run the trading bot
    def run(self):
        # Initialise variables
        AUD = 100.0     # starting AUD holdings
        BTC = 0.0       # starting BTC holdings
        buy_triggered = False
        prices = self.data.loc[:,'close']
        volumes = self.data.loc[:,'volume']
        
        # Store indicators in the dataframe
        for p in self.P:
            if (len(p) == 1):
                continue
            type = p[0]
            if type == "macd":
                macd_indicator = ta.trend.MACD(close=prices, window_slow=p[2], window_fast=p[3], window_sign=p[4])
                self.data.loc[:,'macd']     = macd_indicator.macd()
                self.data.loc[:,'macd_sig'] = macd_indicator.macd_signal()
            elif type == "rsi":
                rsi_indicator = ta.momentum.RSIIndicator(close=prices, window=p[2])
                self.data.loc[:,'rsi'] = rsi_indicator.rsi()
            elif type == "bb":
                bb_indicator = ta.volatility.BollingerBands(close=prices, window=p[2], window_dev=p[3])
                self.data.loc[:,'bb_lower'] = bb_indicator.bollinger_lband()
                self.data.loc[:,'bb_upper'] = bb_indicator.bollinger_hband()
            elif type == "sma":
                sma_indicator_lower = ta.trend.SMAIndicator(close=prices, window=p[2])
                self.data.loc[:,'sma_low'] = sma_indicator_lower.sma_indicator()
                sma_indicator_upper = ta.trend.SMAIndicator(close=prices, window=p[3])
                self.data.loc[:,'sma_upp'] = sma_indicator_upper.sma_indicator()
            elif type == "obv":
                obv_indicator = ta.volume.OnBalanceVolumeIndicator(close=prices, volume=volumes)
                self.data.loc[:,'obv'] = obv_indicator.on_balance_volume()
                self.obv_window = p[2]
        
        # Loop through each day in the data
        for t in range(len(self.data)):
            # Check if a buy trigger occurs and there is no concurrent sell trigger
            if self.buy_trigger(t, self.P) and not buy_triggered:
                buy_triggered = True
                BTC = AUD * 0.98 / self.data.loc[t,'close']
                AUD = 0.0
                # print("{} btc {}".format(t, BTC))
            # Check if a sell trigger occurs and there is no concurrent buy trigger
            elif self.sell_trigger(t, self.P) and buy_triggered:
                buy_triggered = False
                AUD = BTC * 0.98 * self.data.loc[t,'close']
                BTC = 0.0
                # print("{} aud {}".format(t, AUD))
            # Sell remaining BTC at the end of the test period
            if t == len(self.data)-1 and BTC > 0:
                AUD = BTC * 0.98 * self.data.loc[t,'close']
                BTC = 0.0
            self.prev_buy = self.current_buy
            self.prev_sell = self.current_sell
            
            # Store holdings over time for plotting
            if AUD == 0:
                self.aud_holdings.append(BTC * self.data.loc[t,'close'])
            elif BTC == 0:
                self.aud_holdings.append(AUD)
        return AUD

    def plotAUD(self):
        plt.plot(range(len(self.data)), self.aud_holdings)
        plt.title("Best bot performance over 720 candles")
        plt.xlabel('Time')
        plt.ylabel('AUD holdings')
        plt.show()
        
# Retrieve OHLCV data
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
# a = TradingBot([["macd",True, 11,23,12],["rsi", True, 10, 30, 70], ['obv', False,60], ["bb", False, 21, 2]], TEST)
# print(a.run())
# a.plotAUD()