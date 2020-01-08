from sys import maxsize
from time import time
from random import random, randint, sample
from haversine import haversine
import numpy as np
import json



class Individual:  # Route: possible solution to TSP
    def __init__(self, genes):
        assert(len(genes) > 3)
        self.genes = genes
        self.__reset_params()

    def swap(self, gene_1, gene_2):
        self.genes[0]
        a, b = self.genes.index(gene_1), self.genes.index(gene_2)
        self.genes[b], self.genes[a] = self.genes[a], self.genes[b]
        self.__reset_params()

    def add(self, gene):
        self.genes.append(gene)
        self.__reset_params()

    @property
    def fitness(self):
        if self.__fitness == 0:
            self.__fitness = 1 / self.travel_cost  # Normalize travel cost
        return self.__fitness

    @property
    def travel_cost(self):  # Get total travelling cost
        if self.__travel_cost == 0:
            for i in range(len(self.genes)):
                origin = self.genes[i]
                if i == len(self.genes) - 1:
                    dest = self.genes[0]
                else:
                    dest = self.genes[i+1]

                self.__travel_cost += origin.get_distance_to(dest)
                
        return self.__travel_cost

    def __reset_params(self):
        self.__travel_cost = 0
        self.__fitness = 0

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



class Population:  # Population of individuals
    def __init__(self, individuals):
        self.individuals = individuals

    @staticmethod
    def gen_individuals(sz, genes):

        individuals = []        
        _temp = genes[1:]

        for _ in range(sz):
            individual = []
            individual.append(genes[0])
            _individual = sample(_temp, len(_temp))
            for i in _individual:
                individual.append(i)
            individuals.append(Individual(individual))

        return Population(individuals)

    def add(self, route):
        self.individuals.append(route)

    def rmv(self, route):
        self.individuals.remove(route)

    def get_fittest(self):
        fittest = self.individuals[0]
        for route in self.individuals:
            if route.fitness > fittest.fitness:
                fittest = route

        return fittest


def evolve(pop, tourn_size, mut_rate):
    new_generation = Population([])
    pop_size = len(pop.individuals)
    elitism_num = pop_size // 2

    # Elitism
    for _ in range(elitism_num):
        fittest = pop.get_fittest()
        new_generation.add(fittest)
        pop.rmv(fittest)

    # Crossover
    for _ in range(elitism_num, pop_size):
        parent_1 = selection(new_generation, tourn_size)
        parent_2 = selection(new_generation, tourn_size)
        child = crossover(parent_1, parent_2)
        new_generation.add(child)

    # Mutation
    for i in range(elitism_num, pop_size):
        mutate(new_generation.individuals[i], mut_rate)

    return new_generation


def crossover(parent_1, parent_2):
    def fill_with_parent1_genes(child, parent, genes_n):
        
        start_at = randint(1, len(parent.genes)-genes_n-1)
        finish_at = start_at + genes_n
        for i in range(start_at, finish_at):
                child.genes[i] = parent_1.genes[i]

    def fill_with_parent2_genes(child, parent):
        j = 1
        for i in range(1, len(parent.genes)):
            if child.genes[i] == None:
                while parent.genes[j] in child.genes:
                    j += 1
                child.genes[i] = parent.genes[j]
                j += 1
                
    genes_n = len(parent_1.genes)
    child = Individual([None for _ in range(genes_n)])
    fill_with_parent1_genes(child, parent_1, (genes_n-1) // 2)
    fill_with_parent2_genes(child, parent_2)

    child.genes[0] = parent_1.genes[0]

    return child


def mutate(individual, rate):
    for i in range(1, len(individual.genes)):
        if random() < rate:
            _temp = individual.genes[1:]
            sel_genes = sample(_temp, 2)
            if(not (sel_genes[0].getId() == 0 or sel_genes[1].getId() == 0) ):
                individual.swap(sel_genes[0], sel_genes[1])


def selection(population, competitors_n):
    return Population(sample(population.individuals, competitors_n)).get_fittest()


def run_ga(genes, pop_size, n_gen, tourn_size, mut_rate, verbose=1):
    population = Population.gen_individuals(pop_size, genes)
    history = {'cost': [population.get_fittest().travel_cost]}
    counter, generations, min_cost = 0, 0, maxsize

    if verbose:
        print("-- TSP-GA -- Initiating evolution...")

    start_time = time()
    while counter < n_gen:
        population = evolve(population, tourn_size, mut_rate)
        cost = population.get_fittest().travel_cost

        if cost < min_cost:
            counter, min_cost = 0, cost
        else:
            counter += 1

        generations += 1
        history['cost'].append(cost)

    total_time = round(time() - start_time, 6)

    if verbose:
        print("-- TSP-GA -- Evolution finished after {} generations in {} s".format(generations, total_time))
        print("-- TSP-GA -- Minimum travelling cost {} KM".format(min_cost))

    history['generations'] = generations
    history['total_time'] = total_time
    history['route'] = population.get_fittest()

    return history