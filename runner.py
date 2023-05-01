import ccxt
import pandas as pd

from ga import GeneticAlgorithm

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
    MUTATION_RATE   = 0.1
    CROSSOVER_RATE  = 0.8
    DATA = getOHLCVdata()
    ga = GeneticAlgorithm(POPULATION_SIZE, NUM_GENERATIONS, MUTATION_RATE, CROSSOVER_RATE, DATA)
    print(ga.run())

