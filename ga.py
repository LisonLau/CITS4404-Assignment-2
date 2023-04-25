import random
import pandas as pd

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
        self.PARAMETER_RANGES = {
            'window_slow': range(26, 50),
            'window_fast': range(12, 25),
            'window_sign': range(9, 15)
        }
        
    def run(self):
        # Generate an initial population of bots with different parameters
        population = []
        for n in range(self.population_size):
            # Gets random parameters within the ranges specified
            w_slow = random.choice(self.PARAMETER_RANGES['window_slow'])
            w_fast = random.choice(self.PARAMETER_RANGES['window_fast'])
            w_sign = random.choice(self.PARAMETER_RANGES['window_sign'])
            P = [w_slow, w_fast, w_sign]
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
        while len(offspring) < self.population_size:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            child1, child2 = self.crossover(parent1, parent2)
            offspring.extend([self.mutation(child1), self.mutation(child2)])
        return offspring
    
    # Crossover function
    def crossover(self, parent1, parent2):
        child1 = parent1.copy()
        child2 = parent2.copy()
        if random.random() < self.crossover_rate:
            crossover_point = random.randint(1, len(parent1[1]) - 1)
            child1[1][:crossover_point] = parent2[1][:crossover_point]
            child2[1][:crossover_point] = parent1[1][:crossover_point]
        return (child1, child2)
    
    # Mutation function
    def mutation(self, bot):
        mutated_bot = bot.copy()
        for i in range(len(mutated_bot[1])):
            if random.random() < self.mutation_rate:
                if i == 0:
                    mutated_bot[1][i] = random.choice(self.PARAMETER_RANGES['window_slow'])
                elif i == 1:
                    mutated_bot[1][i] = random.choice(self.PARAMETER_RANGES['window_fast'])
                elif i == 2:
                    mutated_bot[1][i] = random.choice(self.PARAMETER_RANGES['window_sign'])
        return mutated_bot
