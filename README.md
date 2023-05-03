# A Genetic Algorithm to Optimise a Bitcoin Trading Bot

Optimises a BTC/AUD bot through its indicators and their parameters using Genetic Algorithms (GA). 

## Installation 

#### Prerequisites 
- [Python 3](https://www.python.org/downloads/)
- [TA library](https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html)
- [ccxt Library](https://github.com/ccxt/ccxt)
- [Pandas](https://pandas.pydata.org/)

Download and install [python 3](https://www.python.org/downloads/).

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

In the terminal where the code is located, run the following code:

```bash
python3 runner.py
```

The GA is set to run a simulation of 30 generations with a population size of 100. 
The default mutation and crossover rate is set at 0.3 and 0.5 initially. 
These values can be changed in runner.py (lines 22-25). 
