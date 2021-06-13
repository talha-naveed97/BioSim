# -*- coding: utf-8 -*-

"""
This module implements the Cell class representing a single square (or cell) on Rossumøya island.
There are four subclasses in this module which represent the four types of cells on the island viz.
Water, Desert, Highland, and Lowland.

"""

from .animals import Herbivore, Carnivore


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
            Dictionary {'f_max': value} that sets the new default value of fodder a cell.

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
            if x['species'] == 'Herbivore':
                obj = Herbivore(x['age'], x['weight'])
                self.herbivores.append(obj)
            else:
                obj = Carnivore(x['age'], x['weight'])
                self.carnivores.append(obj)

    def animals_feed(self):
        for animal in self.herbivores:
            self.food_status = animal.feeds(self.food_status)
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
            self.herbivores.sort(key=lambda x: x.fitness, reverse=False)
            if not continue_eating_cycle:
                break

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
        self.food_status = self.f_max

    def cell_annual_lifecycle(self):
        # Feeding
        self.animals_feed()
        # Procreation
        self.animals_procreate(len(self.herbivores), len(self.carnivores))
        # Migration Flag,
        self.animals_migrate()
        # Aging and weight loss
        self.animals_age()
        # Death
        self.animals_death()

        return [a.fitness for a in self.herbivores], \
               [a.fitness for a in self.carnivores], \
               [a.age for a in self.herbivores], \
               [a.age for a in self.carnivores], \
               [a.weight for a in self.herbivores], \
               [a.weight for a in self.carnivores]


    def get_migration_possibilities(self):
        """

        Returns a list of tuples indicating locations where animal can migrate (see figure 1)

        .. figure:: cells.png
            :width: 200

        Figure 1: Cells where animals can migrate, no diagonal movement.

        |

        """
        return [(self.loc[0] - 1, self.loc[1]), (self.loc[0] + 1, self.loc[1]),
                (self.loc[0], self.loc[1] - 1), (self.loc[0], self.loc[1] + 1)]

    def reset_cell(self):
        """

        Reset the amount of fodder available in cells.

        |

        """
        self.food_status = self.f_max


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
    if land_type == 'H':
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

    if land_type == 'H':
        Highland.update_defaults(params)
    elif land_type == 'L':
        Lowland.update_defaults(params)
    elif land_type == 'D':
        Desert.update_defaults(params)
    elif land_type == 'W':
        raise ValueError('Water cannot have food')
    else:
        raise ValueError('Cannot Identify Land Type')
