# -*- coding: utf-8 -*-

"""
This module implements the Cell class representing a single square (or cell) on Rossumøya island.
There are four subclasses in this module which represent the four types of cells on the island viz.
Water, Desert, Highland, and Lowland.

"""

from .animals import Herbivore, Carnivore, set_animal_params


class Cell:
    """
    The Cell class.

    Attributes
    ----------------
    loc
        Tuple indicating location of cell on the island, starts at (1,1).
    herbivores
        List of herbivores present in the cell.
    carnivores
        List of carnivores present in the cell.
    food_status
        Amount of food available in the cell.

        |

    """

    def __init__(self, loc):
        self.loc = loc
        self.herbivores = []
        self.carnivores = []
        self.food_status = self.f_max

    @classmethod
    def update_defaults(cls, params):
        """
        Update default amount of fodder for cells.

        Parameters
        ----------
        params
            Dictionary {'f_max': value} that sets the new default value of fodder in a cell.

            |

        """
        cls.f_max = params["f_max"]

    def add_animal(self, animals):
        """

        Add animals to their corresponding list (herbivores or carnivores).

        Parameters
        ----------
        animals
            list of dictionaries that specify the species, age, and weight of each animal.

            |

        """
        for x in animals:
            if x['species'] not in ['Herbivore', 'Carnivore']:
                raise KeyError('Invalid key for species. Valid keys are: Herbivore and Carnivore ')
            elif x['species'] == 'Herbivore':
                obj = Herbivore(x['age'], x['weight'])
                self.herbivores.append(obj)
            elif x['species'] == 'Carnivore':
                obj = Carnivore(x['age'], x['weight'])
                self.carnivores.append(obj)

    def animals_feed(self):
        for animal in self.herbivores:
            self.food_status = animal.feeds(self.food_status)
        # Sort animals in cell by fitness
        self.carnivores.sort(key=lambda x: x.fitness, reverse=True)
        for animal in self.carnivores:
            self.herbivores.sort(key=lambda x: x.fitness, reverse=False)
            animal.feeds(self.herbivores)
            self.herbivores = [_herb for _herb in self.herbivores if not _herb.dead]


    def animals_procreate(self, number_of_herbivores, number_of_carnivores):
        index = 0
        while index < len(self.herbivores):
            animal = self.herbivores[index]
            baby = animal.procreation(number_of_herbivores)
            if baby is not None:
                self.herbivores.append(baby)
            index += 1
        index = 0
        while index < len(self.carnivores):
            animal = self.carnivores[index]
            baby = animal.procreation(number_of_carnivores)
            if baby is not None:
                self.carnivores.append(baby)
            index += 1

    def animals_migrate(self):
        for animal in self.herbivores + self.carnivores:
            animal.migration()

    def animals_age(self):
        for animal in self.herbivores + self.carnivores:
            animal.commence_aging()

    def animals_death(self):
        for animal in self.herbivores + self.carnivores:
            animal.death()

        self.herbivores = [herbivore for herbivore in self.herbivores if not herbivore.dead]
        self.carnivores = [carnivore for carnivore in self.carnivores if not carnivore.dead]

    def reset_cell(self):
        """

        Reset the amount of fodder available in cells.

        |

        """
        self.food_status = self.f_max

    # def cell_annual_lifecycle(self):
    #     """
    #     Run the annual cycle for a single cell in following order:
    #         - Feeding
    #         - Procreating
    #         - Migration
    #         - Aging
    #         - Loss of weight
    #         - Death
    #
    #     Returns
    #     -------
    #     list
    #         Fitness values of herbivores
    #     list
    #         Fitness values of carnivores
    #     list
    #         Ages of herbivores
    #     list
    #         Ages of carnivores
    #     list
    #         Weights of herbivores
    #     list
    #         Weights of carnivores
    #
    #         |
    #
    #     """
    #

    def get_migration_possibilities(self):
        """

        Returns a list of tuples indicating locations where animal can migrate (see figure 1)

        .. figure:: cells.png
            :width: 200

        Figure 2: Cells where animals can migrate, no diagonal movement.

        |

        """
        return [(self.loc[0] - 1, self.loc[1]), (self.loc[0] + 1, self.loc[1]),
                (self.loc[0], self.loc[1] - 1), (self.loc[0], self.loc[1] + 1)]


class Water(Cell):
    """

    'Water' cell type: does not allow animals to enter and has no fodder.

    |

    """
    f_max = 0.
    allows_animal = False
    rgb = (0.0, 0.0, 1.0)


class Lowland(Cell):
    """

    'Lowland' cell type: allows animals to enter and has fodder.

    |

    """
    f_max = 800.
    allows_animal = True
    rgb = (0.0, 0.6, 0.0)


class Highland(Cell):
    """

    'Highland' cell type: allows animals to enter and has less fodder than Lowland.

    |

    """
    f_max = 300.
    allows_animal = True
    rgb = (0.5, 1.0, 0.5)


class Desert(Cell):
    """

    'Desert' cell type: allows animals to enter, but has no fodder.

    |

    """
    f_max = 0.
    allows_animal = True
    rgb = (1.0, 1.0, 0.5)


def set_cell_params(land_type, params):
    """

    Set the maximum amount of fodder in cells.

    Parameters
    ----------
    land_type : str
        {'L' for Lowland, 'H' for Highland}

    params : dict
        {'f_max': value}, specifies the new default value of fodder in
        Lowland and Highland cell types.

        |

    """

    if land_type not in ['H', 'L', 'D', 'W']:
        raise KeyError('Invalid keys for land_tpe.')

    if 'f_max' not in params.keys():
        raise KeyError('Invalid keys for params. Only valid key is ''f_max''')

    if land_type in ['D', 'W']:
        raise KeyError('Invalid key for land_tpe. Desert and Water cells have no fodder.')

    if type(params['f_max']) != int and type(params['f_max']) != float or params['f_max'] < 0:
        raise ValueError('f_max must be numeric and cannot be negative.')

    if land_type == 'H' and 'f_max' in params.keys():
        Highland.update_defaults(params)
    elif land_type == 'L' and 'f_max' in params.keys():
        Lowland.update_defaults(params)
    elif land_type == 'D':
        Desert.update_defaults(params)
    elif land_type == 'W':
        raise ValueError('Water cannot have food')
    else:
        raise ValueError('Cannot Identify Land Type')


def update_animal_params(species, params):
    set_animal_params(species, params)
