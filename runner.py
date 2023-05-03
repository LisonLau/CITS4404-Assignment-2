import pandas as pd
import ccxt
import header

from ga import GeneticAlgorithm
from bot import TradingBot

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

if __name__ == '__main__':
    # Define genetic algorithm parameters
    POPULATION_SIZE = 20
    NUM_GENERATIONS = 50
    MUTATION_RATE   = 0.3
    CROSSOVER_RATE  = 0.5
    DATA = getOHLCVdata()
    TRAINING_DATA = DATA.loc[:539,:]
    TEST_DATA = DATA.loc[540:,:]
    ga = GeneticAlgorithm(POPULATION_SIZE, NUM_GENERATIONS, MUTATION_RATE, CROSSOVER_RATE, TRAINING_DATA)
    best_bot = ga.run()
    bot = TradingBot(best_bot[1], TEST_DATA)
    print("Training data over 540 candles")
    print(best_bot)
    print("Running bot over 180 candles")
    print(bot.run())

