# -*- coding: utf-8 -*-
import random

import numpy as np
import matplotlib.pyplot as plt
from .animals import set_animal_params
from .Cells import set_cell_params
from .Island import Island


class BioSim:
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
        self.island = Island(island_map)

    def set_animal_parameters(self, species, params):
        """
        Set parameters for animal species.
        :param species: String, name of animal species
        :param params: Dict with valid parameter specification for species
        """
        set_animal_params(species,params)


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
        for x in range(num_years):
            year_number = x+1
            print("Year:", year_number)
            self.island.commence_annual_cycle(year_number)
            self.num_animals

    def add_population(self,population):
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

    def make_movie(self):
        """Create MPEG4 movie from visualization images saved."""
