# -*- coding: utf-8 -*-

"""
Test set for BioSim class interface for INF200 January 2021.
"""

from src.biosim.animals import *


def test_update_params():
    custom_value = 7.5
    animal = Herbivore(10, 20)
    params = {'zeta': custom_value}
    Herbivore.update_defaults(params)
    assert animal.guideline_params['zeta'] == custom_value


def test_calculate_fitness():
    age = 10
    weight = 20
    animal = Herbivore(10, 20)
    q_age = 1 / (1 + math.exp(animal.guideline_params["phi_age"] * (age - animal.guideline_params["a_half"])))
    q_weight = 1 / (1 + math.exp(
        animal.guideline_params["phi_weight"] * (weight - animal.guideline_params["w_half"])))
    fitness = q_age * q_weight
    animal.calculate_fitness()
    assert animal.fitness == fitness


def test_migration(mocker):
    animal = Herbivore(10, 20)
    animal.calculate_fitness()
    migration_prob = animal.guideline_params["mu"] * animal.fitness
    val = migration_prob - 0.01
    mocker.patch('random.random', return_value=val)
    animal.migration()
    assert animal.migrates == True