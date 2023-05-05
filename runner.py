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
    POPULATION_SIZE = 50
    NUM_GENERATIONS = 25
    MUTATION_RATE   = 0.2
    CROSSOVER_RATE  = 0.5
    
    # Get the training data and testing data
    DATA = getOHLCVdata()
    TRAIN_DATA = DATA.loc[:539,:]
    TEST_DATA  = DATA.loc[540:,:]
    TRAIN = TRAIN_DATA.copy()
    TEST  = TEST_DATA.copy().reset_index()
    
    # Run genetic algorithm to get the 'best bot' found
    ga = GeneticAlgorithm(POPULATION_SIZE, NUM_GENERATIONS, MUTATION_RATE, CROSSOVER_RATE, TRAIN)
    best_bot = ga.run()
    
    # Create an instance of the 'best bot' found and run it with the test data
    best_bot_instance = TradingBot(best_bot[1], TEST)
    best_bot_finalAUD = best_bot_instance.run()
    
    # Print statements 
    print("====================================================================================")
    print("Training bot over 540 candles")
    print("Best bot's final AUD holdings =", best_bot[0])
    print("Best bot's parameters =", best_bot[1])
    print("====================================================================================")
    print("Testing bot over 180 candles")
    print("Best bot's final AUD holdings =", best_bot_finalAUD)
    print("====================================================================================")

    # Plot graphs
    best_bot_instance.plotAUD()
    ga.plotAverageProfit()
    ga.plotBestProfit()
