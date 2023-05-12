# A Genetic Algorithm to Optimise a Bitcoin Trading Bot

This code represents a genetic algorithm-based trading bot for the BTC/AUD trading pair on the Kraken exchange. The bot uses historical OHLCV (Open, High, Low, Close, Volume) data to make buy and sell decisions based on a set of technical indicators.

## Dependencies 

- [Python 3](https://www.python.org/downloads/)
- [TA library](https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html)
- [ccxt Library](https://github.com/ccxt/ccxt)
- [Pandas](https://pandas.pydata.org/)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/LisonLau/CITS4404-Assignment-2.git
```

2. Download and install [python 3](https://www.python.org/downloads/).

Use the package manager pip3 to install the prerequisite packages. 

```bash 
pip3 install ta
```

```bash 
pip3 install ccxt
```

```bash 
pip3 install pandas
```

## Usage

1. In the terminal where the code is located, run the following code:

```bash
python3 runner.py
```

2. The program will retrieve historical data for the BTC/AUD trading pair from the Kraken exchange, split it into training and testing data, and run a genetic algorithm to determine the best set of technical indicator parameters for the trading bot.

3. After the genetic algorithm has completed, the program will create an instance of the "best bot" found and run it using the testing data. The final AUD holdings of the bot will be printed to the console.

## Customisation

The genetic algorithm parameters can be customized in the runner.py (lines 22-25). The default values are:

* POPULATION_SIZE = 100
* NUM_GENERATIONS = 30
* MUTATION_RATE = 0.1
* CROSSOVER_RATE = 0.5
