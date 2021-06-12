# -*- coding: utf-8 -*-
import random

import numpy as np
import matplotlib.pyplot as plt
from .animals import set_animal_params
from .cells import set_cell_params
from .island import Island


class BioSim:
    default_cmax = {'Herbivore': 200, 'Carnivore': 50}
    default_hist_specs = {'fitness': {'max': 1.0, 'delta': 0.05},
                          'age': {'max': 60.0, 'delta': 2},
                          'weight': {'max': 60, 'delta': 2}}

    def __init__(self, island_map, ini_pop, seed,
                 vis_years=1, ymax_animals=None, cmax_animals=None, hist_specs=None,
                 img_dir=None, img_base=None, img_fmt='png', img_years=None,
                 log_file=None):
        """
        :param island_map: Multi-line string specifying island geography
        :param ini_pop: List of dictionaries specifying initial population
        :param seed: Integer used as random number seed
        :param ymax_animals: Number specifying y-axis limit for graph showing animal numbers
        :param cmax_animals: Dict specifying color-code limits for animal densities
        :param hist_specs: Specifications for histograms, see below
        :param vis_years: years between visualization updates (if 0, disable graphics)
        :param img_dir: String with path to directory for figures
        :param img_base: String with beginning of file name for figures
        :param img_fmt: String with file type for figures, e.g. ’png’
        :param img_years: years between visualizations saved to files (default: vis_years)
        :param log_file: If given, write animal counts to this file
        If ymax_animals is None, the y-axis limit should be adjusted automatically.
        If cmax_animals is None, sensible, fixed default values should be used.
        cmax_animals is a dict mapping species names to numbers, e.g.,
        {’Herbivore’: 50, ’Carnivore’: 20}
        hist_specs is a dictionary with one entry per property for which a histogram shall be shown.
        For each property, a dictionary providing the maximum value and the bin width must be
        given, e.g.,
        {’weight’: {’max’: 80, ’delta’: 2}, ’fitness’: {’max’: 1.0, ’delta’: 0.05}}
        Permitted properties are ’weight’, ’age’, ’fitness’.
        If img_dir is None, no figures are written to file. Filenames are formed as
        f’{os.path.join(img_dir, img_base}_{img_number:05d}.{img_fmt}’
        where img_number are consecutive image numbers starting from 0.
        img_dir and img_base must either be both None or both strings.
        """
        self.ini_pop = ini_pop
        self.seed = seed
        if cmax_animals is None:
            self.c_max_animal = self.default_cmax
        else:
            self.c_max_animal = cmax_animals

        if hist_specs is None:
            self.hist_specs = self.default_hist_specs
        else:
            self.hist_specs = hist_specs

        self.island = Island(island_map)

        if ini_pop is not None:
            self.add_population(ini_pop)

    def set_animal_parameters(self, species, params):
        """
        Set parameters for animal species.
        :param species: String, name of animal species
        :param params: Dict with valid parameter specification for species
        """
        set_animal_params(species, params)

    def set_landscape_parameters(self, landscape, params):
        """
        Set parameters for landscape type.
        :param landscape: String, code letter for landscape
        :param params: Dict with valid parameter specification for landscape
        """
        set_cell_params(landscape, params)

    def simulate(self, num_years):
        """
        Run simulation while visualizing the result.
        :param num_years: number of years to simulate
        """
        # print(self.row)
        # print(self.cols)
        # image = np.zeros(self.row * self.cols)
        # image[::2] = np.random.random(self.row * self.cols // 2 + 1)
        #
        # # Reshape things into a 9x9 grid.
        # image = image.reshape((self.row, self.cols))
        # plt.matshow(image)
        # plt.show()
        random.seed(self.seed)
        self.island.setup_visualization(3, 3, num_years, self.c_max_animal,self.hist_specs)
        for x in range(num_years):
            year_number = x + 1
            print("Year:", year_number)
            self.island.commence_annual_cycle(year_number)
            annual_herbivore_count, annual_carnivore_count = self.num_animals_per_species
            # self.island.update_number_of_species_graph(year_number, num_years, annual_herbivore_count,
            #                                            annual_carnivore_count)
            # herbivore_distribution, carnivore_distribution = self.island.get_distributions()
            # self.island.update_system_map(herbivore_distribution, carnivore_distribution, self.c_max_animal)
            # self.island.fitness_histogram(year_number, self.hist_specs['fitness'])
            # self.island.age_histogram(year_number, self.hist_specs['age'])
            # self.island.weight_histogram(year_number, self.hist_specs['weight'])
            self.island.update_visualiztion(year_number,num_years,annual_herbivore_count,annual_carnivore_count,
                                            self.c_max_animal,self.hist_specs)

    def add_population(self, population):
        """
        Add a population to the island
        :param population: List of dictionaries specifying population
        """
        self.island.add_population(population)

    @property
    def year(self):
        """Last year simulated."""


    @property
    def num_animals(self):
        """Total number of animals on island."""

    @property
    def num_animals_per_species(self):
        """Number of animals per species in island, as dictionary."""
        annual_herbivore_count, annual_carnivore_count = self.island.get_total_species_count()
        print(annual_herbivore_count, annual_carnivore_count)
        return annual_herbivore_count, annual_carnivore_count

    def make_movie(self):
        """Create MPEG4 movie from visualization images saved."""
