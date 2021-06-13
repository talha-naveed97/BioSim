# -*- coding: utf-8 -*-

import math
import random


class Animals:
    def __init__(self, age, weight):
        self.age = age
        self.weight = weight
        self.fitness = 0
        self.calculate_fitness()
        self.migrates = False
        self.dead = False

    @classmethod
    def update_defaults(cls, params):
        key_diff = params.keys() - cls.guideline_params.keys()
        if len(key_diff) != 0:
            raise ValueError('The following keys are invalid: ', key_diff)
        if 'DeltaPhiMax' in params.keys() and params['DeltaPhiMax'] <= 0:
            raise ValueError('DeltaPhiMax must be > zero')
        for key, value in params.items():
            if type(value) is not int and type(value) is not float:
                raise ValueError('All parameter values must be numerical')
            if value < 0:
                raise ValueError('All parameter values must be >= zero')
        cls.guideline_params.update(params)

    def calculate_fitness(self):
        if self.weight <= 0:
            self.fitness = 0
        else:
            q_age = 1 / (1 + math.exp(self.guideline_params["phi_age"] * (self.age - self.guideline_params["a_half"])))
            q_weight = 1 / (1 + math.exp(-
                                         self.guideline_params["phi_weight"] * (
                                                 self.weight - self.guideline_params["w_half"])))
            self.fitness = q_age * q_weight

    def procreation(self, cell_animal_count):
        birth_prob = 0
        if cell_animal_count > 1 and self.weight >= self.guideline_params["zeta"] * (self.guideline_params["w_birth"]
                                                                                     + self.guideline_params[
                                                                                         "sigma_birth"]):
            birth_prob = min(1, self.guideline_params["gamma"] * self.fitness * (cell_animal_count - 1))
        if birth_prob > random.random():
            baby_age = 0
            baby_weight = random.gauss(self.guideline_params["w_birth"], self.guideline_params["sigma_birth"])
            mother_weight_loss = self.guideline_params["xi"] * baby_weight
            if self.weight >= mother_weight_loss:
                baby = self.__class__(baby_age, baby_weight)
                self.weight -= mother_weight_loss
                self.calculate_fitness()
                return baby
        return None

    def migration(self):
        migration_prob = self.guideline_params["mu"] * self.fitness
        if migration_prob > random.random():
            self.migrates = True
        else:
            self.migrates = False

    def commence_aging(self):
        self.age += 1
        self.weight -= self.weight * self.guideline_params["eta"]
        self.calculate_fitness()

    def death(self):
        death_prob = 0
        if self.weight <= 0:
            self.dead = True
        else:
            death_prob = self.guideline_params["omega"] * (1 - self.fitness)

        if death_prob > random.random():
            self.dead = True


class Herbivore(Animals):

    def __init__(self, age, weight):
        super().__init__(age, weight)

    guideline_params = {'w_birth': 8.0,
                        'sigma_birth': 1.5,
                        'beta': 0.9,
                        'eta': 0.05,
                        'a_half': 40.0,
                        'phi_age': 0.6,
                        'w_half': 10.0,
                        'phi_weight': 0.1,
                        'mu': 0.25,
                        'gamma': 0.2,
                        'zeta': 3.5,
                        'xi': 1.2,
                        'omega': 0.4,
                        'F': 10.0,
                        'DeltaPhiMax': None
                        }

    def feeds(self, cell_food_amount):
        f = self.guideline_params["F"]
        if f > cell_food_amount:
            f = cell_food_amount
        self.weight += f * self.guideline_params["beta"]
        self.calculate_fitness()
        feed_left = cell_food_amount - f
        return feed_left


class Carnivore(Animals):

    def __init__(self, age, weight):
        super().__init__(age, weight)

    guideline_params = {'w_birth': 6.0,
                        'sigma_birth': 1.0,
                        'beta': 0.75,
                        'eta': 0.125,
                        'a_half': 40.0,
                        'phi_age': 0.3,
                        'w_half': 4.0,
                        'phi_weight': 0.4,
                        'mu': 0.4,
                        'gamma': 0.8,
                        'zeta': 3.5,
                        'xi': 1.1,
                        'omega': 0.8,
                        'F': 50.0,
                        'DeltaPhiMax': 10.0
                        }

    def feeds(self, herbivores):
        continue_eating_cycle = True
        amount_eaten = 0
        for herbivore in herbivores:
            fitness_difference = self.fitness - herbivore.fitness
            if self.fitness <= herbivore.fitness:
                continue_eating_cycle = False
                break
            elif 0 < fitness_difference < self.guideline_params["DeltaPhiMax"]:
                eating_probability = fitness_difference / self.guideline_params["DeltaPhiMax"]
            else:
                eating_probability = 1

            if eating_probability > random.random():
                herbivore.dead = True
                self.weight += self.guideline_params["beta"] * herbivore.weight
                amount_eaten += herbivore.weight
                self.calculate_fitness()
                if amount_eaten >= self.guideline_params["F"]:
                    break
        return continue_eating_cycle


def set_animal_params(species, params):
    if species == 'Herbivore':
        Herbivore.update_defaults(params)
    elif species == 'Carnivore':
        Carnivore.update_defaults(params)
    else:
        raise ValueError('Cannot Identify Species')
