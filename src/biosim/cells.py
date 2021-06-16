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
    ----------
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
        params : dict
            Dictionary {'f_max': *value*} that sets the new default value of fodder in a cell.


        .. code-block:: python

            params = {'f_max': 500}
            Lowland.update_defaults(params)


        |

        """
        if len(params.keys()) > 1:
            raise ValueError('Cell accepts only one key i.e f_max')
        valid_key = {'f_max': None}
        key_diff = params.keys() - valid_key.keys()
        if len(key_diff) != 0:
            raise ValueError('Key value is invalid: ', key_diff)
        value = params['f_max']
        if type(value) is not int and type(value) is not float:
            raise ValueError('f_max must be numerical')
        if value < 0:
            raise ValueError('f_max cannot be less than zero')
        cls.f_max = params["f_max"]

    def add_animal(self, animals):
        """

        Add animals to their corresponding list (herbivores or carnivores) in Cell class.

        Parameters
        ----------
        animals : list
            list of dictionaries that specify the species, age, and weight of each animal.

        .. code-block:: python

            lowland = Lowland(10,10)
            herb = [{'species': 'Herbivore', 'age': 1, 'weight': 10} for _ in range(5)]
            carn = [{'species': 'Carnivore', 'age': 2, 'weight': 5} for _ in range(7)]
            lowland.add_animal(herb)
            lowland.add_animal(carn)


        |

        """
        try:
            for x in animals:
                if x['species'] not in ['Herbivore', 'Carnivore']:
                    raise KeyError('Invalid key for species. Valid keys are: Herbivore and Carnivore ')
                elif x['species'] == 'Herbivore':
                    obj = Herbivore(x['age'], x['weight'])
                    self.herbivores.append(obj)
                elif x['species'] == 'Carnivore':
                    obj = Carnivore(x['age'], x['weight'])
                    self.carnivores.append(obj)
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while adding animal to cell: {}'.format(err))

    def animals_feed(self):
        """
        Animals feeding in a cell.

            .. seealso::
                - biosim.animals.Herbivore.feeds()
                - biosim.animals.Carnivore.feeds()


        .. code-block:: python

            lowland = Lowland(10,10)
            herb = [{'species': 'Herbivore', 'age': 1, 'weight': 10} for _ in range(5)]
            carn = [{'species': 'Carnivore', 'age': 2, 'weight': 5} for _ in range(7)]
            lowland.add_animal(herb)
            lowland.add_animal(carn)
            lowland.animals_feed()

        |

        """
        try:
            for animal in self.herbivores:
                self.food_status = animal.feeds(self.food_status)
            # Sort animals in cell by fitness
            self.carnivores.sort(key=lambda x: x.fitness, reverse=True)
            for animal in self.carnivores:
                self.herbivores.sort(key=lambda x: x.fitness, reverse=False)
                animal.feeds(self.herbivores)
                self.herbivores = [_herb for _herb in self.herbivores if not _herb.dead]
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while animal feeding cycle: {}'.format(err))

    def animals_procreate(self, number_of_herbivores, number_of_carnivores):
        """
        Animals procreating in a cell.

            .. seealso::
                - biosim.animals.Animals.procreation()

        .. code-block:: python

            lowland = Lowland(10,10)
            herb = [{'species': 'Herbivore', 'age': 1, 'weight': 10} for _ in range(5)]
            carn = [{'species': 'Carnivore', 'age': 2, 'weight': 5} for _ in range(7)]
            lowland.add_animal(herb)
            lowland.add_animal(carn)
            lowland.animals_procreate()


        |

        """
        try:
            index = 0
            newborn_herbivores = []
            newborn_carnivores = []
            while index < len(self.herbivores):
                animal = self.herbivores[index]
                baby = animal.procreation(number_of_herbivores)
                if baby is not None:
                    newborn_herbivores.append(baby)
                index += 1
            index = 0
            while index < len(self.carnivores):
                animal = self.carnivores[index]
                baby = animal.procreation(number_of_carnivores)
                if baby is not None:
                    newborn_carnivores.append(baby)
                index += 1
            return newborn_herbivores, newborn_carnivores
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while animal procreation cycle: {}'.format(err))

    def animals_migrate(self):
        """
        Animals migrating from one cell to another.

            .. seealso::
                - biosim.animals.Animals.migration()


        .. code-block:: python

            lowland = Lowland(10,10)
            herb = [{'species': 'Herbivore', 'age': 1, 'weight': 10} for _ in range(5)]
            carn = [{'species': 'Carnivore', 'age': 2, 'weight': 5} for _ in range(7)]
            lowland.add_animal(herb)
            lowland.add_animal(carn)
            lowland.animals_migrate()


        |

        """
        try:
            for animal in self.herbivores + self.carnivores:
                animal.migration()
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while animal migrating cycle: {}'.format(err))

    def animals_age(self):
        """
        Animals aging.

            .. seealso::
                - biosim.animals.Animals.commence_aging()


        .. code-block:: python

            lowland = Lowland(10,10)
            herb = [{'species': 'Herbivore', 'age': 1, 'weight': 10} for _ in range(5)]
            carn = [{'species': 'Carnivore', 'age': 2, 'weight': 5} for _ in range(7)]
            lowland.add_animal(herb)
            lowland.add_animal(carn)
            lowland.animals_age()


        |

        """
        try:
            for animal in self.herbivores + self.carnivores:
                animal.commence_aging()
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while animal aging cycle: {}'.format(err))

    def animals_death(self):
        """
        Animals dying.

            .. seealso::
                - biosim.animals.Animals.death()


        .. code-block:: python

            lowland = Lowland(10,10)
            herb = [{'species': 'Herbivore', 'age': 1, 'weight': 10} for _ in range(5)]
            carn = [{'species': 'Carnivore', 'age': 2, 'weight': 5} for _ in range(7)]
            lowland.add_animal(herb)
            lowland.add_animal(carn)
            lowland.animals_death()


        |

        """
        try:
            for animal in self.herbivores + self.carnivores:
                animal.death()

            self.herbivores = [herbivore for herbivore in self.herbivores if not herbivore.dead]
            self.carnivores = [carnivore for carnivore in self.carnivores if not carnivore.dead]
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while animal death cycle: {}'.format(err))

    def reset_cell(self):
        """

        Reset the amount of fodder available in cells to their *f_max*.


        .. code-block:: python

            lowland = Lowland(10,10)
            lowland.reset_cell()


        |

        """
        self.food_status = self.f_max

    def get_migration_possibilities(self):
        """

        Returns a list of four tuples representing locations where animal can migrate to
        from the current cell. (see figure 1)

        .. figure:: ../../cells.png
            :width: 200

        Figure 2: Cells where animals can migrate, no diagonal movement.


        .. code-block:: python

            cell = Lowland(10,10)
            cell.reset_cell()


        |

        """
        return [(self.loc[0] - 1, self.loc[1]), (self.loc[0] + 1, self.loc[1]),
                (self.loc[0], self.loc[1] - 1), (self.loc[0], self.loc[1] + 1)]


class Water(Cell):
    """

    'Water' cell type: does not allow animals to enter and has no fodder.


     .. code-block:: python

            water = Water(10,10)


    |

    """
    f_max = 0.
    allows_animal = False
    rgb = (0.0, 0.0, 1.0)


class Lowland(Cell):
    """

    'Lowland' cell type: allows animals to enter and has fodder.

     .. code-block:: python

        lowland = Lowland(10,10)


    |

    """
    f_max = 800.
    allows_animal = True
    rgb = (0.0, 0.6, 0.0)


class Highland(Cell):
    """

    'Highland' cell type: allows animals to enter and has less fodder than Lowland.


    .. code-block:: python

        highland = Highland(10,10)


    |

    """
    f_max = 300.
    allows_animal = True
    rgb = (0.5, 1.0, 0.5)


class Desert(Cell):
    """

    'Desert' cell type: allows animals to enter, but has no fodder.


    .. code-block:: python

        desert = Desert(10,10)


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

        .. seealso::
            - Cell.update_defaults()


    .. code-block:: python

        set_cell_params('D', {'f_max': 10.})


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
    """
    Update animal parameters.

        .. seealso::
            - biosim.animals.set_animal_params()

    |

    """
    set_animal_params(species, params)
