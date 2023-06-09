import random
import header
import numpy as np
import matplotlib.pyplot as plt
import copy

from bot import TradingBot

class GeneticAlgorithm:
    
    # Constructor for GeneticAlgorithm
    def __init__(self, population_size, num_generations, mutation_rate, crossover_rate, data):
        self.population_size = population_size
        self.mutation_rate   = mutation_rate
        self.crossover_rate  = crossover_rate
        self.num_generations = num_generations
        self.data = data
        self.avg_fitness_scores  = []
        self.best_fitness_scores = []
        
        # Define the range of parameter values for the MACD indicator
        self.MACD_RANGES = {
            'window_slow': range(26, 51),
            'window_fast': range(12, 26),
            'window_sign': range(9, 15)
        }
        
        # Define the range of parameter values for the RSI indicator
        self.RSI_RANGES = {
            'window': range(10, 25),
            'oversold': range(20, 50),
            'overbought': range(50, 101)
        }
        
        # Define the range of parameter values for the BB indicator
        self.BB_RANGES = {
            'window'    : range(20, 30),
            'window_dev': range(2, 3)
        }
        
        # Define the range of parameter values for the SMA indicator
        self.SMA_RANGES = {
            'window_low': range(20, 150),
            'window_upp': range(150, 250)
        }
        
        # Define the range of parameter values for the OBV indicator 
        self.OBV_RANGES = {
            'window': range(10, 101)
        }

    def run(self): 
        # Generate an initial population of bots with different parameters
        population = []
        for n in range(self.population_size):
            # Gets random parameters within the ranges specified
            P = self.getIndicatorCombination()
            bot = TradingBot(P, self.data)  # Returns finalAUD
            botInstance = [bot.run(), P]
            population.append(botInstance)

        # Run the genetic algorithm for number of generations
        for g in range(self.num_generations):
            # Evaluate fitness of the initial population
            fitness_scores = self.evaluate_fitness(population)
            
            # Select the top performing bots
            parents = self.select_parents(population, fitness_scores)
            
            # Create offspring through crossover and mutation
            offspring = self.reproduce(parents)
            
            for x in offspring:
                bot = TradingBot(x[1], self.data)
                x[0] = bot.run()
            
            # Replace the old population with the new one
            population = offspring
            
            print(f"\n-~-~-~-~-~-~-~-~-~-~-~-~-~-Generation {g+1}-~-~-~-~-~-~-~-~-~-~-~-~-~-")
            # Get average profit of all bots in the population
            all_profits = np.array(fitness_scores)
            mean_profit = np.mean(all_profits)
            self.avg_fitness_scores.append(mean_profit)
            print(f"Average profit =", mean_profit)
            
            # Get the best performing bot in the population
            fitness_scores = self.evaluate_fitness(population)
            best_bot_index = fitness_scores.index(max(fitness_scores))
            best_bot = population[best_bot_index]  
            self.best_fitness_scores.append(best_bot[0])
            print(f"Best bot found =", best_bot)
        
        return best_bot
    
    # Returns 1 or 0
    def one_or_zero(self):
        if random.random() < 0.5:
            return 1
        else:
            return 0
    
    # Get random combination of indicators with random parameters within the ranges
    def getIndicatorCombination(self):
        trend       = self.getTrend(0)
        momentum    = self.getMomentum(0)
        volume      = self.getVolume(0)
        volatility  = self.getVolatility(0)
        P = [trend, momentum, volume, volatility]
        return P
    
    # TREND INDICATORS
    def getTrend(self, start):
        numTrend = random.randint(start, len(header.TREND)-1)
        if numTrend == 0:
            return [header.TREND[numTrend]]
        elif numTrend == 1:
            w_slow = random.choice(self.MACD_RANGES['window_slow'])
            w_fast = random.choice(self.MACD_RANGES['window_fast'])
            w_sign = random.choice(self.MACD_RANGES['window_sign'])
            macd = [header.TREND[numTrend], self.one_or_zero(), w_slow, w_fast, w_sign]
            return macd
        elif numTrend == 2:
            window_low = random.choice(self.SMA_RANGES['window_low'])
            window_upp = random.choice(self.SMA_RANGES['window_upp'])
            sma = [header.TREND[numTrend], self.one_or_zero(), window_low, window_upp]
            return sma
            
    # MOMENTUM INDICATORS
    def getMomentum(self, start):
        numMomentum = random.randint(start, len(header.MOMENTUM)-1)
        if numMomentum == 0:
            return [header.MOMENTUM[numMomentum]]
        elif numMomentum == 1:
            window = random.choice(self.RSI_RANGES['window'])
            ovsold = random.choice(self.RSI_RANGES['oversold'])
            ovbought = random.choice(self.RSI_RANGES['overbought'])
            rsi = [header.MOMENTUM[numMomentum], self.one_or_zero(), window, ovsold, ovbought]
            return rsi
        
    # VOLUME INDICATORS
    def getVolume(self, start):
        numVolume = random.randint(start, len(header.VOLUME)-1)
        if numVolume == 0:
            return [header.VOLUME[numVolume]]
        elif numVolume == 1:
            window = random.choice(self.OBV_RANGES['window'])
            obv = [header.VOLUME[numVolume], self.one_or_zero(), window]
            return obv
    
    # VOLATILITY INDICATORS
    def getVolatility(self, start):
        numVolatiltiy = random.randint(start, len(header.VOLATILITY)-1)
        if numVolatiltiy == 0:
            return [header.VOLATILITY[numVolatiltiy]]
        elif numVolatiltiy == 1:
            window = random.choice(self.BB_RANGES['window'])
            w_dev  = random.choice(self.BB_RANGES['window_dev'])
            bb = [header.VOLATILITY[numVolatiltiy], self.one_or_zero(), window, w_dev]
            return bb
        
    # Calculate fitness function
    def calculate_fitness(self, bot_final_AUD):
        profit = bot_final_AUD - 100.0
        return profit
        
    # Evaluate fitness of each bot in the population
    def evaluate_fitness(self, population):
        return [self.calculate_fitness(bot[0]) for bot in population]
       
    # Select parents of the next generation
    def select_parents(self, population, fitness_scores):
        elite_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:self.population_size // 2]
        elite_bots = [population[i] for i in elite_indices]
        return elite_bots
    
    # Create offspring by applying through genetic operators crossover and mutation
    def reproduce(self, parents):
        new_population = copy.deepcopy(parents)
        offspring = []
        while len(offspring) < self.population_size // 2:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            child1, child2 = self.crossover(parent1, parent2)
            child1 = self.mutation(child1)
            child2 = self.mutation(child2)
            offspring.append(child1)
            offspring.append(child2)
        new_population.extend(offspring)
        return new_population
    
    # Crossover function
    def crossover(self, parent1, parent2):
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        for i in range(4):
            if random.random() < self.crossover_rate:
                a = child1[1][i]
                b = child2[1][i]
                child2[1][i] = a
                child1[1][i] = b
        return (child1, child2)
    
    # Mutation function
    def mutation(self, bot):
        mutated_bot = copy.deepcopy(bot)

        # [TREND, MOMENTUM, VOLUME, VOLATILITY]
        for i in range(4):
            if mutated_bot[1][i][0] == "":
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i] = self.introduceIndicator(i)
            elif mutated_bot[1][i][0] == "macd":
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][1] = not mutated_bot[1][i][1]
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][2] = random.choice(self.MACD_RANGES['window_slow'])
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][3] = random.choice(self.MACD_RANGES['window_fast'])
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][4] = random.choice(self.MACD_RANGES['window_sign'])
            elif mutated_bot[1][i][0] == "sma":
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][1] = not mutated_bot[1][i][1]
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][2] = random.choice(self.SMA_RANGES['window_low'])
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][3] = random.choice(self.SMA_RANGES['window_upp'])
            elif mutated_bot[1][i][0] == "rsi":
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][1] = not mutated_bot[1][i][1]
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][2] = random.choice(self.RSI_RANGES['window'])
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][3] = random.choice(self.RSI_RANGES['oversold'])
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][4] = random.choice(self.RSI_RANGES['overbought'])
            elif mutated_bot[1][i][0] == "obv":
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][1] = not mutated_bot[1][i][1]
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][2] = random.choice(self.OBV_RANGES['window'])
            elif mutated_bot[1][i][0] == "bb":
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][1] = not mutated_bot[1][i][1]
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][2] = random.choice(self.BB_RANGES['window'])
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][3] = random.choice(self.BB_RANGES['window_dev'])
   
        return mutated_bot
    
    def introduceIndicator(self, idx):
        if idx == 0: # TREND
            trend = self.getTrend(1)
            return trend
        elif idx == 1: # MOMENTUM
            momentum = self.getMomentum(1)
            return momentum
        elif idx == 2: # VOLUME
            volume = self.getVolume(1)
            return volume
        elif idx == 3: # VOLATILITY
            volatility = self.getVolatility(1)
            return volatility
        
    def plotAverageProfit(self):
        plt.plot(range(self.num_generations), self.avg_fitness_scores)
        plt.title('Average Fitness Score over Generations')
        plt.xlabel('Generation')
        plt.ylabel('Fitness Score (Profit)')
        plt.show()
        
    def plotBestValue(self):
        plt.plot(range(self.num_generations), self.best_fitness_scores)
        plt.title('Best bot performance over Generations')
        plt.xlabel('Generation')
        plt.ylabel('AUD holdings')
        plt.show()