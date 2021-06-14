# -*- coding: utf-8 -*-

"""
This module implements the Island class that models the complete geography of Rossumøya island.

        .. figure:: island.png
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
    img_fmt :
        File format of the image.

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
                - cells.set_cell_params()


        |

        """
        set_cell_params(landscape, params)

    @staticmethod
    def update_animal_params(species, params):
        """
        Update default characteristics of animals.

        .. seealso::
                - cells.update_animal_params(species, params)
                - animals.set_animal_params(species, params)

        |

        """
        update_animal_params(species, params)

    def add_population(self, species):
        """
        Add population (herbivores and carnivores) to the cells on the island.

        .. seealso::
                - cells.add_animal(animals)

        |

        """
        for record in species:
            loc = record['loc']
            animals = record['pop']
            cell = [item for item in self.cell_list
                    if item.loc[0] == loc[0] and item.loc[1] == loc[1]][0]
            cell.add_animal(animals)

    def commence_annual_cycle(self):
        """
               Run the annual lifecycle of cells on the island.

               .. seealso::
                       - cells.cell_annual_lifecycle()

               |

               """
        self.reset_annual_stats()
        for cell in self.cell_list:
            if not cell.allows_animal:
                continue
            cell.animals_feed()

        for cell in self.cell_list:
            if not cell.allows_animal:
                continue
            cell.animals_procreate(len(cell.herbivores), len(cell.carnivores))

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

    def reset_annual_stats(self):
        self.fitness_values = {"Herbivore": [],
                               "Carnivore": []}
        self.age_values = {"Herbivore": [],
                           "Carnivore": []}
        self.weight_values = {"Herbivore": [],
                              "Carnivore": []}

    def animal_migrates(self, cell):
        for animal in cell.herbivores + cell.carnivores:
            if animal.migrated:
                continue
            animal.migration()
            if animal.migrates:
                possible_locations = cell.get_migration_possibilities()
                migration_destination = self.get_random_cell(possible_locations)
                migrating_cell = [cl for cl in self.cell_list
                                  if cl.loc[0] == migration_destination[0] and
                                  cl.loc[1] == migration_destination[1]][0]
                if not migrating_cell.allows_animal:
                    continue
                else:
                    animal.migrated = True
                    if animal.__class__.__name__ == 'Herbivore':
                        migrating_cell.herbivores.append(animal)
                        cell.herbivores.pop(cell.herbivores.index(animal))
                    elif animal.__class__.__name__ == 'Carnivore':
                        migrating_cell.carnivores.append(animal)
                        cell.carnivores.pop(cell.carnivores.index(animal))
        return None

    @staticmethod
    def get_random_cell(possibilities):
        _dir = random.randint(0, 3)
        return possibilities[_dir]

    def get_total_species_count(self):
        total_herbivores = sum(len(c.herbivores) for c in self.cell_list)
        total_carnivores = sum(len(c.carnivores) for c in self.cell_list)
        return {'Herbivore': total_herbivores, 'Carnivore': total_carnivores}

    def get_total_animal_count(self):
        total_animals = sum(len(c.herbivores) + len(c.carnivores) for c in self.cell_list)
        return total_animals

    def setup_visualization(self, rows, cols, total_years, cmap, hist_specs, y_max, img_years):
        herb_dist, carn_dist = self.get_distributions()
        self.graphics.setup_visualization(rows, cols, total_years,
                                          cmap, hist_specs, y_max,
                                          img_years, self.map_rgb,
                                          herb_dist, carn_dist)

    def update_visualization(self, year, total_years, herbivore_count, carnivores_count,
                             cmax_animals, hist_specs, y_max):
        herbivore_dist, carnivore_dist = self.get_distributions()
        herbivore_date = {
            "count": herbivore_count,
            "fitness": self.fitness_values["Herbivore"],
            "age": self.age_values["Herbivore"],
            "weight": self.weight_values["Herbivore"],
            "distribution": herbivore_dist
        }

        carnivore_date = {
            "count": carnivores_count,
            "fitness": self.fitness_values["Carnivore"],
            "age": self.age_values["Carnivore"],
            "weight": self.weight_values["Carnivore"],
            "distribution": carnivore_dist
        }
        self.graphics.update_visualization(year, total_years, cmax_animals, hist_specs, y_max,
                                           herbivore_date, carnivore_date)

    def get_distributions(self):
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
                cell = [item for item in self.cell_list
                        if item.loc[0] == loc[0] and item.loc[1] == loc[1]][0]
                row_list_herbivore.append(len(cell.herbivores))
                row_list_carnivore.append(len(cell.carnivores))
            herbivore_dist.append(row_list_herbivore)
            carnivore_dist.append(row_list_carnivore)
        return herbivore_dist, carnivore_dist

    def make_movie(self):
        self.graphics.make_movie()
