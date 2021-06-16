# -*- coding: utf-8 -*-

"""
This module implements the Island class that models the complete geography of Rossumøya island.

        .. figure:: ../../sphx_glr_island.png
            :width: 300

            Figure 1: Geography of Rossumøya island in *check_sim.py*
"""

from .cells import Water, Lowland, Highland, Desert, set_cell_params, update_animal_params
import random
from .graphics import Graphics


class Island:
    """
    The Island class.

    Parameters
    ----------
    geo : str
        String where each character represents the landscape of each cell on the island.
    img_dir : str
        Path to the directory where images from the simulation are saved.
    img_name : str
        Filenames of images.
    img_fmt : str
        File format of the image.

        |

    Attributes
    ----------
    fitness_values
        *dict*: Dictionary with keys 'Herbivore' and 'Carnivore' indicating type of animal.
        Each key corresponds to a list of fitness values for every animal on the island
        that belongs to that type.

        |

    age_values
        *dict*: Dictionary with keys 'Herbivore' and 'Carnivore' indicating type of animal.
        Each key corresponds to a list of age values for every animal on the island
        that belongs to that type.

        |

    weight_values
        *dict*: Dictionary with keys 'Herbivore' and 'Carnivore' indicating type of animal.
        Each key corresponds to a list of weight values for every animal on the island
        that belongs to that type.

        |

    """

    def __init__(self, geo, img_dir=None, img_name=None, img_fmt=None):
        self.geo = geo
        self.map_rgb = []
        self.cell_list = []
        self.add_cells()
        self.graphics = Graphics(img_dir, img_name, img_fmt)
        self.fitness_values = {"Herbivore": [],
                               "Carnivore": []}
        self.age_values = {"Herbivore": [],
                           "Carnivore": []}
        self.weight_values = {"Herbivore": [],
                              "Carnivore": []}

    def add_cells(self):
        """
        Add cells to the Island model.

        |

        """
        try:
            map_list = self.geo.splitlines()
            rows = len(map_list)
            for row in range(1, rows + 1):
                rgb_cells_in_row = []
                line = map_list[row - 1].strip()
                chars = len(line)
                if row > 1 and chars != len(map_list[row - 2]):
                    raise ValueError('Inconsistent row length')

                for col in range(1, chars + 1):
                    land_type = line[col - 1]
                    if (row == 1 or row == rows or col == 1 or col == chars) \
                            and land_type != 'W':
                        raise ValueError('Cannot have non ocean boundry')
                    loc = (row, col)
                    if land_type == 'W':
                        cell = Water(loc)
                    elif land_type == 'H':
                        cell = Highland(loc)
                    elif land_type == 'L':
                        cell = Lowland(loc)
                    elif land_type == 'D':
                        cell = Desert(loc)
                    else:
                        raise ValueError('Cannot Identify Land Type')
                    rgb_cells_in_row.append(cell.rgb)
                    self.cell_list.append(cell)
                self.map_rgb.append(rgb_cells_in_row)
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed to add cells in island: {}'.format(err))

    @staticmethod
    def update_cell_params(landscape, params):
        """
        Update default parameters of cells.

        Parameters
        ----------
        landscape : str
            Defines the cell type.

        params : dict
            Dictionary {*f_max*: value} that sets the new default value of fodder in a cell.


        .. seealso::
                - biosim.cells.set_cell_params()


        .. code-block:: python

            island = Island(map)
            island.update_cell_params('L', {'f_max': 700})


        |

        """
        set_cell_params(landscape, params)

    @staticmethod
    def update_animal_params(species, params):
        """
        Update default characteristics of animals.

        .. seealso::
                - biosim.cells.update_animal_params(species, params)
                - biosim.animals.set_animal_params(species, params)


        .. code-block:: python

            island = Island(map)
            island.update_cell_params('Herbivore', {'zeta': 3.2, 'xi': 1.8})



        |

        """
        update_animal_params(species, params)

    def add_population(self, population):
        """
        Add population (herbivores and/or carnivores) to the cells on the island.


        Parameters
        ----------
        population : list
            list of dictionaries where each dictionary has two keys: 'loc' specifying the
            cell location where animal are to be added, and 'pop' specifying the species,
            age, and weight of the animals to be added on the island.


        .. seealso::
                - biosim.cells.add_animal(animals)



        .. code-block:: python

            island = Island(map)
            ini_carns = [{'loc': (10, 10),
                  'pop': [{'species': 'Carnivore',
                           'age': 5,
                           'weight': 20}
                          for _ in range(40)]}]
            island..add_population(ini_carns)


        |

        """
        try:
            for record in population:
                loc = record['loc']
                animals = record['pop']
                cell = next((item for item in self.cell_list if item.loc[0] == loc[0]
                             and item.loc[1] == loc[1]), None)
                if cell is None:
                    raise RuntimeError("Cell Not Found!", cell)
                cell.add_animal(animals)
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed to add population in island: {}'.format(err))

    def commence_annual_cycle(self):
        """
        Run the annual cycle for a single cell in following order:
            - Feeding
            - Procreating
            - Migration
            - Aging
            - Death

               .. seealso::
                       - biosim.cells.animals_feed()
                       - biosim.cells.animals_procreate()
                       - Island.animal_migrates()
                       - biosim.cells.animals_age()
                       - biosim.cells.animals_death()


        .. code-block:: python


            island = Island(map)
            ini_carns = [{'loc': (10, 10),
            'pop': [{'species': 'Carnivore','age': 5,'weight': 20}
             for _ in range(40)]}]

            island..add_population(ini_carns)
            island.commence_annual_cycle()


        |
        """
        try:
            self.reset_annual_stats()
            for cell in self.cell_list:
                if not cell.allows_animal:
                    continue
                cell.animals_feed()

            for cell in self.cell_list:
                if not cell.allows_animal:
                    continue
                baby_herbivores, baby_carnivores = cell.animals_procreate(len(cell.herbivores),
                                                                          len(cell.carnivores))
                cell.herbivores.extend(baby_herbivores)
                cell.carnivores.extend(baby_carnivores)

            for cell in self.cell_list:
                if not cell.allows_animal:
                    continue
                self.animal_migrates(cell)

            for cell in self.cell_list:
                if not cell.allows_animal:
                    continue
                cell.animals_age()

            for cell in self.cell_list:
                if not cell.allows_animal:
                    continue
                cell.animals_death()
                cell.reset_cell()
                self.fitness_values["Herbivore"].extend([o.fitness for o in cell.herbivores])
                self.fitness_values["Carnivore"].extend([o.fitness for o in cell.carnivores])
                self.weight_values["Herbivore"].extend([o.weight for o in cell.herbivores])
                self.weight_values["Carnivore"].extend([o.weight for o in cell.carnivores])
                self.age_values["Herbivore"].extend([o.age for o in cell.herbivores])
                self.age_values["Carnivore"].extend([o.age for o in cell.carnivores])
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while commencing cycle: {}'.format(err))

    def reset_annual_stats(self):
        """
        Reset Island attributes to intial values.

        |

        """
        self.fitness_values = {"Herbivore": [],
                               "Carnivore": []}
        self.age_values = {"Herbivore": [],
                           "Carnivore": []}
        self.weight_values = {"Herbivore": [],
                              "Carnivore": []}

    def animal_migrates(self, cell):
        """
        Migration of animals that can migrate to cells that allow animals to enter.

               .. seealso::
                       - biosim.cells.get_migration_possibilities()
                       - biosim.animals.Animals.migration()

        |

        """
        try:
            for animal in cell.herbivores + cell.carnivores:
                if animal.has_migrated:
                    continue
                animal.migration()
                if animal.can_migrate:
                    possible_locations = cell.get_migration_possibilities()
                    migration_destination = self.get_random_cell(possible_locations)
                    migrating_cell = next((item for item in self.cell_list
                                           if item.loc[0] == migration_destination[0]
                                           and item.loc[1] == migration_destination[1]), None)
                    if migrating_cell is None:
                        raise RuntimeError("Cell Not Found!", cell)
                    if not migrating_cell.allows_animal:
                        continue
                    else:
                        animal.has_migrated = True
                        if animal.__class__.__name__ == 'Herbivore':
                            migrating_cell.herbivores.append(animal)
                            cell.herbivores.pop(cell.herbivores.index(animal))
                        elif animal.__class__.__name__ == 'Carnivore':
                            migrating_cell.carnivores.append(animal)
                            cell.carnivores.pop(cell.carnivores.index(animal))
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed during migration: {}'.format(err))
        return None

    @staticmethod
    def get_random_cell(possibilities):
        _dir = random.randint(0, 3)
        return possibilities[_dir]

    def get_total_species_count(self):
        """
        Returns a dictionary with counts of herbivores and carnivores on the island.

        .. code-block:: python


            island = Island(map)
            ini_carns = [{'loc': (10, 10),
                          'pop': [{'species': 'Carnivore',
                                   'age': 5,
                                   'weight': 20}
                                  for _ in range(40)]}]
            ini_herbs = [{'loc': (10, 10),
                          'pop': [{'species': 'Herbivore',
                                   'age': 5,
                                   'weight': 20}
                                  for _ in range(40)]}]
            island..add_population(ini_carns + ini_herbs)
            counts = island.get_total_species_count()
            print("Herbivores:", counts["Herbivore"])
            print("Carnivore:", counts["Carnivore"])


        |

        """
        total_herbivores = sum(len(c.herbivores) for c in self.cell_list)
        total_carnivores = sum(len(c.carnivores) for c in self.cell_list)
        return {'Herbivore': total_herbivores, 'Carnivore': total_carnivores}

    def get_total_animal_count(self):
        """
        Returns the total number of animals on the island.


        .. code-block:: python


            island = Island(map)
            ini_carns = [{'loc': (10, 10),
                          'pop': [{'species': 'Carnivore',
                                   'age': 5,
                                   'weight': 20}
                                  for _ in range(40)]}]
            ini_herbs = [{'loc': (10, 10),
                          'pop': [{'species': 'Herbivore',
                                   'age': 5,
                                   'weight': 20}
                                  for _ in range(40)]}]
            island..add_population(ini_carns + ini_herbs)
            count = island.get_total_animal_count()
            print("Total Animals:", count)


        |

        """
        total_animals = sum(len(c.herbivores) + len(c.carnivores) for c in self.cell_list)
        return total_animals

    def setup_visualization(self, total_years, cmax, hist_specs, y_max, img_years):
        """
        Sets up the graphics for the project.

        Parameters
        ----------
        total_years : int
            Total number of years to simulate
        cmax : dict
            cmap dictionary for animals
        hist_specs : dict
            histogram specs for bins calculation
        y_max: int
            Max peak value for number of species graph
        img_years: int
            interval for saving images


        .. code-block:: python


            island = Island(map)
            island.add_population(ini_carns + ini_herbs)
            island.setup_visualization(20, {'Herbivore': 200, 'Carnivore': 50},
                                        {'fitness': {'max': 1.0, 'delta': 0.05},
                                          'age': {'max': 60.0, 'delta': 2},
                                          'weight': {'max': 60, 'delta': 2}}
                                          , 20000, 1)


        |

        """
        try:
            map = self.geo.splitlines()
            herb_dist = [[0] * len(map[0].strip()) for i in range(len(map))]
            carn_dist = [[0] * len(map[0].strip()) for i in range(len(map))]
            self.graphics.setup_visualization(total_years,
                                              cmax, hist_specs, y_max,
                                              img_years, self.map_rgb,
                                              herb_dist, carn_dist)
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while initializing graphics: {}'.format(err))

    def update_visualization(self, year, total_years, animal_counts,
                             cmax_animals, hist_specs, y_max):
        """
                Sets up the graphics for the project.

                Parameters
                ----------
                year : int
                    Current year
                total_years : int
                    Total number of years to simulate
                animal_counts: dict
                    Species count dictionary
                cmax_animals : dict
                    cmax dictionary for animals
                hist_specs : dict
                    histogram specs for bins calculation
                y_max: int
                    Max peak value for number of species graph


                .. code-block:: python


                    island = Island(map)
                    island.add_population(ini_carns + ini_herbs)
                    island.update_visualization(1,20,5,5 {'Herbivore': 200, 'Carnivore': 50},
                                                {'fitness': {'max': 1.0, 'delta': 0.05},
                                                  'age': {'max': 60.0, 'delta': 2},
                                                  'weight': {'max': 60, 'delta': 2}}
                                                  , 20000)


                |

                """
        try:
            herbivore_dist, carnivore_dist = self.get_distributions()
            herbivore_date = {
                "count": animal_counts['Herbivore'],
                "fitness": self.fitness_values["Herbivore"],
                "age": self.age_values["Herbivore"],
                "weight": self.weight_values["Herbivore"],
                "distribution": herbivore_dist
            }

            carnivore_date = {
                "count": animal_counts['Carnivore'],
                "fitness": self.fitness_values["Carnivore"],
                "age": self.age_values["Carnivore"],
                "weight": self.weight_values["Carnivore"],
                "distribution": carnivore_dist
            }
            self.graphics.update_visualization(year, total_years, cmax_animals, hist_specs, y_max,
                                               herbivore_date, carnivore_date, self.cell_list)
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while updating graphics: {}'.format(err))

    def get_distributions(self):
        """
            Get cell wise distribution for distributions graph

        |

        """
        try:
            map_list = self.geo.splitlines()
            rows = len(map_list)
            herbivore_dist = []
            carnivore_dist = []
            for x in range(rows):
                row_list_carnivore = []
                row_list_herbivore = []
                line = map_list[x].strip()
                chars = len(line)
                for y in range(chars):
                    loc = (x + 1, y + 1)
                    cell = next((item for item in self.cell_list if item.loc[0] == loc[0] and
                                 item.loc[1] == loc[1]), None)
                    if cell is None:
                        raise RuntimeError("Cell Not Found!", cell)
                    row_list_herbivore.append(len(cell.herbivores))
                    row_list_carnivore.append(len(cell.carnivores))
                herbivore_dist.append(row_list_herbivore)
                carnivore_dist.append(row_list_carnivore)
            return herbivore_dist, carnivore_dist
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while getting distributions: {}'.format(err))

    def make_movie(self, movie_format=None):
        """
            Makes video of the images saved during simulation


            island = Island(map)
            island..make_movie('gif')


        |

        """
        try:
            self.graphics.make_movie(movie_format)
        except RuntimeError as err:
            raise RuntimeError('ERROR: Failed while making movie: {}'.format(err))
