import ta

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
                a = self.macd_indicator(t,P)
                lit = a[0] > a[1] and a[2] <= a[3]
            elif (P[i][0] == "bb"):
                pass
            elif (P[i][0] == "rsi"):
                pass
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
                lit = a[0] < a[1] and a[2] >= a[3]
            elif (P[i][0] == "bb"):
                pass
            elif (P[i][0] == "rsi"):
                pass
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
        macd_indicator = ta.trend.MACD(close=prices, window_slow=w_slow, window_fast=w_fast, window_sign=w_sign, fillna= True)
        macd_line      = macd_indicator.macd().loc[t]
        signal_line    = macd_indicator.macd_signal().loc[t]
        if t-1 >= 0:
            prev_macd   = macd_indicator.macd().loc[0] 
            prev_signal = macd_indicator.macd_signal().loc[0]
        else:
            prev_macd   = macd_indicator.macd().loc[0] 
            prev_signal = macd_indicator.macd_signal().loc[0]
        return [macd_line, signal_line, prev_macd, prev_signal]


    def bb_indicator(self,t,P):
        pass

    def rsi_indicator(self,t,P):
        pass

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