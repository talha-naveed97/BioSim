# -*- coding: utf-8 -*-

"""
This module implements the Cell class representing a single square (or cell) on Rossumøya island.
There are four subclasses in this module which represent the four types of cells on the island viz.
Water, Desert, Highland, and Lowland.

"""

from .animals import Herbivore, Carnivore


class Cell:
    """

    Parameters
    ----------
    loc : tuple
        Location of cell on the island.

    Attributes
    ----------------
    herbivores
        List of herbivores present in the cell.
    carnivores
        List of carnivores present in the cell.
    food_status
        Amount of food available in the cell.
    """

    def __init__(self, loc):
        self.loc = loc
        self.herbivores = []
        self.carnivores = []
        self.food_status = self.f_max

    @classmethod
    def update_defaults(cls, params):
        """
        Updates the default amount of fodder for cells.

        Parameters
        ----------
        params : dict
            Dictionary {'f_max': value} that specifies the new default value of fodder in Lowland and Highland
            cell types.
        """
        cls.f_max = params["f_max"]

    def add_animal(self, animals):
        """
        Add animals to their corresponding list (herbivores or carnivores).

        Parameters
        ----------
        animals : list
            list of dictionaries that specify the species, age, and weight of each animal.
        """
        for x in animals:
            if x['species'] == 'Herbivore':
                obj = Herbivore(x['age'], x['weight'])
                self.herbivores.append(obj)
            elif x['species'] == 'Carnivore':
                obj = Carnivore(x['age'], x['weight'])
                self.carnivores.append(obj)

    def calculate_cell_fitness(self):
        for animal in self.herbivores + self.carnivores:
            animal.calculate_fitness()

    def cell_annual_lifecycle(self):
        """
        Runs the annual cycle for the a single cell:
            - Feeding
            - Procreating
            - Migration
            - Aging
            - Loss of weight
            - Death
        """

        # Calculate fitness of Animals in Cell
        self.calculate_cell_fitness()

        # Sort animals in cell by fitness
        self.herbivores.sort(key=lambda x: x.fitness, reverse=False)
        self.carnivores.sort(key=lambda x: x.fitness, reverse=True)

        # Feeding
        for animal in self.herbivores:
            feed_left = animal.feeds(self.food_status)
            self.food_status = feed_left
        for animal in self.carnivores:
            continue_eating_cycle = animal.feeds(self.herbivores)
            self.herbivores = [animal for animal in self.herbivores if not animal.dead]
            if not continue_eating_cycle:
                break

        # Procreation
        newborn_herbivores = []
        newborn_carnivores = []
        for animal in self.herbivores:
            baby = animal.procreation(len(self.herbivores))
            if baby is not None:
                newborn_herbivores.append(baby)
        for animal in self.carnivores:
            baby = animal.procreation(len(self.carnivores))
            if baby is not None:
                newborn_carnivores.append(baby)

        # Migration, Aging, Weight Loss, Death
        for animal in self.herbivores + self.carnivores:
            animal.migration()
            animal.commence_aging()
            animal.commence_weight_loss()
            animal.death()

        # Remove dead animals from List
        self.herbivores = [animal for animal in self.herbivores if not animal.dead]
        self.carnivores = [animal for animal in self.carnivores if not animal.dead]

        # Add Newborns
        self.herbivores.extend(newborn_herbivores)
        self.carnivores.extend(newborn_carnivores)

        return [a.fitness for a in self.herbivores],\
               [a.fitness for a in self.carnivores],\
               [a.age for a in self.herbivores],\
               [a.age for a in self.carnivores],\
               [a.weight for a in self.herbivores],\
               [a.weight for a in self.carnivores],\


    def get_migration_possibilities(self):
        return [(self.loc[0] - 1, self.loc[1]), (self.loc[0] + 1, self.loc[1]),
                (self.loc[0], self.loc[1] - 1), (self.loc[0], self.loc[1] + 1)]

    def reset_cell(self):
        self.food_status = self.f_max


class Water(Cell):
    """
    'Water' cell type, does not allow animals to enter and has no fodder.
    """
    f_max = 0.
    allows_animal = False
    rgb = (0.0, 0.0, 1.0)


class Lowland(Cell):
    """
    'Lowland' cell type, allows animals to enter and has fodder.
    """
    f_max = 800.
    allows_animal = True
    rgb = (0.0, 0.6, 0.0)


class Highland(Cell):
    """
    'Highland' cell type, allows animals to enter and has less fodder than Lowland.
    """
    f_max = 300.
    allows_animal = True
    rgb = (0.5, 1.0, 0.5)


class Desert(Cell):
    """
    'Desert' cell type: allows animals to enter, but has no fodder.
    """
    f_max = 0.
    allows_animal = True
    rgb = (1.0, 1.0, 0.5)


def set_cell_params(land_type, params):
    if land_type == 'W':
        Water.update_defaults(params)
    elif land_type == 'H':
        Highland.update_defaults(params)
    elif land_type == 'L':
        Lowland.update_defaults(params)
    elif land_type == 'D':
        Desert.update_defaults(params)
