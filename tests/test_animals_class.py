# -*- coding: utf-8 -*-

"""
Test set for Animals class for INF200 June 2021.
"""

from biosim import animals
from biosim.animals import Herbivore, Carnivore
import math
import pytest


def test_update_params():
    """
    Test that parameters of animals are updated correctly.
    """

    custom_value = 7.5
    animal = Herbivore(10, 20)
    params = {'zeta': custom_value}
    Herbivore.update_defaults(params)
    assert animal.guideline_params['zeta'] == custom_value


def test_calculate_fitness():
    """
    Test that animal fitness is computed correctly.
    """

    age = 10
    weight = 20
    animal = Herbivore(10, 20)
    q_age = 1 / (1 + math.exp(animal.guideline_params["phi_age"] * (age - animal.guideline_params["a_half"])))
    q_weight = 1 / (1 + math.exp(-
                                 animal.guideline_params["phi_weight"] * (weight - animal.guideline_params["w_half"])))
    fitness = q_age * q_weight
    animal.calculate_fitness()
    assert animal.fitness == fitness


def test_migration(mocker):
    """
    Test that animal is able to migrate if probability is above a certain threshold.
    """

    animal = Carnivore(10, 20)
    animal.calculate_fitness()
    migration_prob = animal.guideline_params["mu"] * animal.fitness
    val = migration_prob - 0.01
    mocker.patch('random.random', return_value=val)
    animal.migration()
    assert animal.migrates is True


def test_aging():
    """
    Test that animal age increases by 1 in one year.
    """
    animal = Herbivore(5, 5)
    animal.commence_aging()
    assert animal.age == 6


def test_death(mocker):
    """
    Test that animal will die if its probability is above a certain threshold.
    """
    animal = Herbivore(6, 12)
    animal.calculate_fitness()
    death_prob = animal.guideline_params["omega"] * (1 - animal.fitness)
    val = death_prob - 0.01
    mocker.patch('random.random', return_value=val)
    animal.death()
    assert animal.dead is True


def test_set_animal_params():
    """
    Test that error is raised is wrong key is given in set_animal_params().
    """
    species = 'wrong_species'
    params = {'age': 10, 'weight': 20}
    with pytest.raises(ValueError):
        animals.set_animal_params(species, params)
