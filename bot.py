import pandas as pd
import ccxt
import ta 
import random

# PARAMETERS TO OPTIMISE
PARAMETER_RANGES = {
    "window_slow": range(13, 52),
    "window_fast": range(6, 24),
    "window_sign": range(4, 18)
}

# GENETIC ALGORITHM PARAMETERS
POPULATION_SIZE = 20
NUM_GENERATIONS = 50
MUTATION_RATE = 0.2
CROSSOVER_RATE = 0.75


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
def trade_bot(P, data):
    # Initialise holdings
    AUD = 100.0     # starting AUD holdings
    BTC = 0.0       # starting BTC holdings
    buy_triggered = False

    for t in range(len(data)):
        if trigger(t, P, data, buy_triggered) == "BUY":
            buy_triggered = True
            AUD_buy = AUD * 0.98
            BTC = AUD_buy / data['close'][t]
            AUD = 0.0
        elif trigger(t, P, data, buy_triggered) == "SELL":
            buy_triggered = False
            BTC_sell = BTC * 0.98
            AUD = BTC_sell * data['close'][t]
            BTC = 0.0
        elif t == len(data)-1 and BTC > 0.0:
            BTC_sell = BTC * 0.98
            AUD = BTC_sell * data['close'][t]
            BTC = 0.0

    return AUD

def fitness(bot_total):
    
    return (bot_total - 100.0)

def crossover(parent1, parent2):
    child1 = parent1.copy()
    child2 = parent2.copy()

    for i in range(len(parent1)):
        if random.random() < CROSSOVER_RATE:
            crossover_point = random.randint(1, len(parent1[1]) - 1)
            child1[1][:crossover_point] = parent2[1][:crossover_point]
            child2[1][:crossover_point] = parent1[1][:crossover_point]

    return child1, child2

def mutation(child):
    mutate_child = child.copy()

    for i in range(len(mutate_child[1])):
        if random.random() < MUTATION_RATE:
            if i == 0:
                mutate_child[1][i] = random.choice(PARAMETER_RANGES['window_slow'])
            elif i == 1:
                mutate_child[1][i] = random.choice(PARAMETER_RANGES['window_fast'])
            elif i == 2:
                mutate_child[1][i] = random.choice(PARAMETER_RANGES['window_sign'])

    return mutate_child


def genetic_alg():
    
    data = getOHLCVdata()
    population = []

    # GENERATE SETS OF PARAMETERS OF VARYING RANGES
    for i in range(POPULATION_SIZE):
        window_slow = random.choice(PARAMETER_RANGES['window_slow'])
        window_fast = random.choice(PARAMETER_RANGES['window_fast'])
        window_signal = random.choice(PARAMETER_RANGES['window_sign'])

        P = [window_slow, window_fast, window_signal]

        strat_outcome = trade_bot(P, data)

        bot_instance = [strat_outcome, P] 

        population.append(bot_instance)

    # Main loop for genetic algorithm
    for g in range(NUM_GENERATIONS):
        #Evaluate fitness of each strategy in the population
        fitness_scores = [fitness(bot[0]) for bot in population]

        # Select the best strategies in the population 
        parents = []

        for i in range(POPULATION_SIZE // 2):
            index = fitness_scores.index(max(fitness_scores))

            parents.append(population[index])
            fitness_scores[index] = 0

        # Create new generation of strategies through crossover and mutation
        new_population = parents.copy()

        while len(new_population) < POPULATION_SIZE:
            child1, child2 = crossover(random.choice(parents), random.choice(parents))
            new_population.extend([mutation(child1), mutation(child2)])
        
        population = new_population

    # Reevaluate new population
    fitness_scores = [fitness(bot[0]) for bot in population]

    # Get the best optimised bot
    optimised_bot_index = fitness_scores.index(max(fitness_scores))
    opt_bot = population[optimised_bot_index]

    return opt_bot





#P = [26, 12, 9, 14]
#data = getOHLCVdata()
#total_earn = trade_bot(P)

opt_bot = genetic_alg()

print("The best bot has a profit of {} with window_slow {}, window_fast {} and window_sign {}".format(
    opt_bot[0], opt_bot[1][0], opt_bot[1][1], opt_bot[1][2])
)