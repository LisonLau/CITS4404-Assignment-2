import ccxt
import ta
import pandas as pd
import random

# Define the range of parameter values for the MACD indicator
PARAMETER_RANGES = {
    'window_slow': range(10, 41),
    'window_fast': range(1, 21),
    'window_sign': range(1, 21)
}

# Define genetic algorithm parameters
POPULATION_SIZE = 2
NUM_GENERATIONS = 1
MUTATION_RATE   = 0.1
CROSSOVER_RATE  = 0.8

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

# Define the buy trigger function using MACD indicator
def buy_trigger(t, P, data):
    # Define MACD parameters from P
    w_slow = int(P[0])
    w_fast = int(P[1])
    w_sign = int(P[2])
    
    # Get close prices data for MACD calculation
    prices = data.loc[:t, 'close']
    
    # Calculate MACD and signal lines for t
    macd_indicator = ta.trend.MACD(close=prices, window_slow=w_slow, window_fast=w_fast, window_sign=w_sign)
    macd_line      = macd_indicator.macd().loc[t]
    signal_line    = macd_indicator.macd_signal().loc[t]
    # prev_macd      = macd_indicator.macd().iloc[t-1] 
    # prev_signal    = macd_indicator.macd_signal().iloc[t-1]
    # Trigger buy signal if MACD line is above signal line
    return (macd_line > signal_line) #and (prev_macd < prev_signal))

# Define the sell trigger function using MACD indicator
def sell_trigger(t, P, data):
    # Define MACD parameters from P
    w_slow = int(P[0])
    w_fast = int(P[1])
    w_sign = int(P[2])
    
    # Get close prices data for MACD calculation
    prices = data.loc[:t, 'close']
    
    # Calculate MACD and signal lines for t
    macd_indicator = ta.trend.MACD(close=prices, window_slow=w_slow, window_fast=w_fast, window_sign=w_sign)
    macd_line      = macd_indicator.macd().loc[t]
    signal_line    = macd_indicator.macd_signal().loc[t]
    # prev_macd      = macd_indicator.macd().loc[t-1] 
    # prev_signal    = macd_indicator.macd_signal().loc[t-1]
    # Trigger sell signal if MACD line is below signal line
    return (macd_line < signal_line) #and (prev_macd > prev_signal))

# Define the trading bot function
# P format = (window_slow, window_fast, window_sign)
def trading_bot(P, data):
    # Initialise variables
    AUD = 100.0     # starting AUD holdings
    BTC = 0.0       # starting BTC holdings
    buy_triggered = False

    # Loop through each day in the data
    for t in range(len(data)):
        # Check if a buy trigger occurs and there is no concurrent sell trigger
        if buy_trigger(t, P, data) and not buy_triggered:
            buy_triggered = True
            BTC = AUD * 0.98 / data['close'][t]
            AUD = 0.0
        # Check if a sell trigger occurs and there is no concurrent buy trigger
        elif sell_trigger(t, P, data) and buy_triggered:
            buy_triggered = False
            AUD = BTC  * 0.98 * data['close'][t]
            BTC = 0.0
        # Sell remaining BTC at the end of the test period
        elif t == len(data)-1 and BTC > 0:
            AUD = BTC * 0.98 * data['close'][t]
            BTC = 0.0
    return AUD

# Define the fitness function
def evaluate_fitness(bot_final_AUD):
    profit = bot_final_AUD - 100.0
    return profit

# Define the crossover function
def crossover(parent1, parent2):
    child1 = parent1.copy()
    child2 = parent2.copy()
    if random.random() < CROSSOVER_RATE:
        crossover_point = random.randint(1, len(parent1[1]) - 1)
        child1[1][:crossover_point] = parent2[1][:crossover_point]
        child2[1][:crossover_point] = parent1[1][:crossover_point]
    return [child1, child2]

# Define the mutation function
def mutation(bot):
    mutated_bot = bot.copy()
    for i in range(len(mutated_bot[1])):
        if random.random() < MUTATION_RATE:
            mutated_bot[1][i] = random.randint(P_MIN, P_MAX)
    return mutated_bot

# Genetic algorithm
def genetic_algorithm():
    # Get same set of data used for all bots 
    data = getOHLCVdata()
    
    # Generate an initial population of bots with different parameters
    population = []
    for n in range(POPULATION_SIZE):
        # Gets random parameters within the ranges specified
        w_slow = random.choice(PARAMETER_RANGES['window_slow'])
        w_fast = random.choice(PARAMETER_RANGES['window_fast'])
        w_sign = random.choice(PARAMETER_RANGES['window_sign'])
        P = (w_slow, w_fast, w_sign)
        bot = trading_bot(P, data)  # Returns finalAUD
        botInstance = (bot, P)      # (finalAUD, (w_slow, w_fast, w_sign))
        population.append(botInstance) 
        
    # Run the genetic algorithm
    for g in range(NUM_GENERATIONS):
        # Evaluate the fitness of each bot in the population
        fitness_scores = [evaluate_fitness(bot(0)) for bot in population]
        print(fitness_scores)
        # Select the top performing bots
        elite_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:POPULATION_SIZE // 2]
        print(elite_indices)
        elite_bots = [population[i] for i in elite_indices]
        print(elite_bots)
        # Apply genetic operators to create a new population
        new_population = elite_bots.copy()
        while len(new_population) < POPULATION_SIZE:
            parent1 = random.choice(elite_bots)
            parent2 = random.choice(elite_bots)
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([mutation(child1), mutation(child2)])
            
        # Replace the old population with the new one
        population = new_population
        
    # Evaluate the fitness of the final population
    fitness_scores = [evaluate_fitness(bot) for bot in population]
    
    # Select the best performing bot and print its parameters and final value
    best_bot_index = fitness_scores.index(max(fitness_scores))
    best_bot = population[best_bot_index]
    return best_bot
    
genetic_algorithm()


