# -*- coding: utf-8 -*-

import math
import random
# from enum import Enum
#
#
# class Animal_Type(Enum):
#     Herbivore = 1
#     Carnivore = 2

class Animals:
    def __init__(self, age, weight):
        self.age = age
        self.weight = weight
        self.dead = False
        self.fitness = 0
        self.migrates = False
        self.gives_birth = False

    @classmethod
    def update_defaults(cls, params):
        cls.guideline_params.update(params)

    def calculate_fitness(self):
        if self.weight <= 0:
            self.fitness = 0
        else:
            q_age = 1 / (1 + math.exp(self.guideline_params["phi_age"] * (self.age - self.guideline_params["a_half"])))
            q_weight = 1 / (1 + math.exp(-
                self.guideline_params["phi_weight"] * (self.weight - self.guideline_params["w_half"])))
            self.fitness = q_age * q_weight

    def migration(self):
        migration_prob = self.guideline_params["mu"] * self.fitness
        if migration_prob > random.random():
            self.migrates = True
        else:
            self.migrates = False

    def birth(self, cell_animal_count):
        if cell_animal_count > 1 and self.weight >= self.guideline_params["zeta"] * (self.guideline_params["w_birth"]
                                                                                     + self.guideline_params[
                                                                                         "sigma_birth"]):
            birth_prob = min(1, self.guideline_params["gamma"] * self.fitness * (cell_animal_count - 1))
        else:
            birth_prob = 0

        if birth_prob > random.random():
            self.gives_birth = True
        else:
            self.gives_birth = False

    def procreation(self, cell_animal_count):
        self.birth(cell_animal_count)
        if self.gives_birth:
            baby_age = 0
            baby_weight = random.gauss(self.guideline_params["w_birth"], self.guideline_params["sigma_birth"])
            mother_weight_loss = self.guideline_params["xi"] * baby_weight
            if self.weight >= mother_weight_loss:
                baby = self.__class__(baby_age, baby_weight)
                baby.calculate_fitness()
                self.weight -= mother_weight_loss
                return baby
            else:
                return None
        else:
            return None

    def death(self):
        if self.weight == 0:
            death_prob = 1
        else:
            death_prob = self.guideline_params["omega"] * (1 - self.fitness)

        if death_prob > random.random():
            self.dead = True
        else:
            self.dead = False

    def commence_aging(self):
        self.age += 1

    def commence_weight_loss(self):
        self.weight -= self.weight * self.guideline_params["eta"]
        if self.weight <= 0:
            self.death()


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
        F = self.guideline_params["F"]
        if F > cell_food_amount:
            F = cell_food_amount
        self.weight += F * self.guideline_params["beta"]
        feed_left = cell_food_amount - F
        if feed_left <= 0:
            feed_left = 0
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
        eating_probability = 0
        continue_eating_cycle = True
        amount_eaten = 0
        for herbivore in herbivores:
            fitness_difference = self.fitness - herbivore.fitness
            if self.fitness <= herbivore.fitness:
                eating_probability = 0
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
    else:
        Carnivore.update_defaults(params)
