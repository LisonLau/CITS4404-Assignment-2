import random
import header

from bot import TradingBot

class GeneticAlgorithm:
    
    # Constructor for GeneticAlgorithm
    def __init__(self, population_size, num_generations, mutation_rate, crossover_rate, data):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.num_generations = num_generations
        self.data = data
        
        # Define the range of parameter values for the MACD indicator
        self.MACD_RANGES = {
            'window_slow': range(26, 50),
            'window_fast': range(12, 25),
            'window_sign': range(9, 15)
        }
        
        # Define the range of parameter values for the RSI indicator
        self.RSI_RANGES = {
            'window': range(10, 25)
        }
        
        # Define the range of parameter values for the BB indicator
        self.BB_RANGES = {
            'window'    : range(20, 30),
            'window_dev': range(2, 3)
        }
        
        # Define the range of parameter values for the SMA indicator
        self.SMA_RANGES = {
            'window': range(20, 200, 10)
        }
        
        # Define the range of parameter values for the OBV indicator 
        self.OBV_RANGES = {
            'window': range(10,100,10)
        }

    def run(self): 
        # Generate an initial population of bots with different parameters
        population = []
        # TODO: include default values in initial population
        for n in range(self.population_size):
            # Gets random parameters within the ranges specified
            P = []
            while len(P) == 0:
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
            
            # Replace the old population with the new one
            population = offspring
            
        # Evaluate the fitness of the final population
        fitness_scores = self.evaluate_fitness(population)
        
        # Return the best performing bot in the final population
        best_bot_index = fitness_scores.index(max(fitness_scores))
        best_bot = population[best_bot_index]
        return best_bot
    
    # Returns 1 or 0
    def one_or_zero(self):
        if random.random() < 0.5:
            return 1
        else:
            return 0
    
    # Get random combination of indicators with random parameters within the ranges
    def getIndicatorCombination(self):
        P = []
        numTrend        = random.randint(0, len(header.TREND)-1)
        numMomentum     = random.randint(0, len(header.MOMENTUM)-1)
        numVolume       = random.randint(0, len(header.VOLUME)-1)
        numVolatiltiy   = random.randint(0, len(header.VOLATILITY)-1)
        
        # TREND INDICATORS
        if numTrend == 0:
            P.append([header.TREND[numTrend]])
        elif numTrend == 1:
            w_slow = random.choice(self.MACD_RANGES['window_slow'])
            w_fast = random.choice(self.MACD_RANGES['window_fast'])
            w_sign = random.choice(self.MACD_RANGES['window_sign'])
            macd = [header.TREND[numTrend], self.one_or_zero(), w_slow, w_fast, w_sign]
            P.append(macd)
        elif numTrend == 2:
            window = random.choice(self.SMA_RANGES['window'])
            sma = [header.TREND[numTrend], self.one_or_zero(), window]
            P.append(sma)
            
        # MOMENTUM INDICATORS
        if numMomentum == 0:
            P.append([header.MOMENTUM[numMomentum]])
        elif numMomentum == 1:
            window = random.choice(self.RSI_RANGES['window'])
            rsi = [header.MOMENTUM[numMomentum], self.one_or_zero(), window]
            P.append(rsi)
            
        # VOLUME INDICATORS
        if numVolume == 0:
            P.append([header.VOLUME[numVolume]])
        elif numVolume == 1:
            window = random.choice(self.OBV_RANGES['window'])
            obv = [header.VOLUME[numVolume], self.one_or_zero(), window]
            P.append(obv)
        
        # VOLATILITY INDICATORS
        if numVolatiltiy == 0:
            P.append([header.VOLATILITY[numVolatiltiy]])
        elif numVolatiltiy == 1:
            window = random.choice(self.BB_RANGES['window'])
            w_dev  = random.choice(self.BB_RANGES['window_dev'])
            bb = [header.VOLATILITY[numVolatiltiy], self.one_or_zero(), window, w_dev]
            P.append(bb)
        
        return P
                
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
        offspring = parents.copy()
        # TODO: fix mutation and crossover to fit the parameters
        while len(offspring) < self.population_size:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            child1, child2 = self.crossover(parent1, parent2)
            offspring.extend([child1, child2])
            offspring.extend([self.mutation(child1), self.mutation(child2)])
        return offspring
    
    # Crossover function
    def crossover(self, parent1, parent2):
        child1 = parent1.copy()
        child2 = parent2.copy()
        for i in range(4):
            if random.random() < self.crossover_rate:
                a = child1[1][i]
                b = child2[1][i]
                child2[1][i] = a
                child1[1][i] = b
        return (child1, child2)
    
    # Mutation function
    def mutation(self, bot):
        mutated_bot = bot.copy()

        for i in range(4):
            if mutated_bot[1][i][0] == "":
                continue
            elif mutated_bot[1][i][0] == "macd":
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][2] = random.choice(self.MACD_RANGES['window_slow'])
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][3] = random.choice(self.MACD_RANGES['window_fast'])
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][2] = random.choice(self.MACD_RANGES['window_sign'])
            elif mutated_bot[1][i][0] == "sma":
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][2] = random.choice(self.SMA_RANGES['window'])
            elif mutated_bot[1][i][0] == "rsi":
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][2] = random.choice(self.RSI_RANGES['window'])
            elif mutated_bot[1][i][0] == "obv":
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][2] = random.choice(self.OBV_RANGES['window'])
            elif mutated_bot[1][i][0] == "bb":
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][2] = random.choice(self.BB_RANGES['window'])
                if random.random() < self.mutation_rate:
                    mutated_bot[1][i][3] = random.choice(self.BB_RANGES['window_dev'])
   
        return mutated_bot
