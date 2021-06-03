# -*- coding: utf-8 -*-
import random

import numpy as np
import matplotlib.pyplot as plt
from .animals import Herbivore,set_params


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
        self.row = len(island_map.splitlines())
        self.cols = len(island_map.splitlines())
        self.cells = [{'animals': [],'f_max' : 500}]
        self.ini_pop = ini_pop
        self.seed = seed

    def set_animal_parameters(self, species, params):
        """
        Set parameters for animal species.
        :param species: String, name of animal species
        :param params: Dict with valid parameter specification for species
        """
        set_params(species,params)


    def set_landscape_parameters(self, landscape, params):
        """
        Set parameters for landscape type.
        :param landscape: String, code letter for landscape
        :param params: Dict with valid parameter specification for landscape
        """


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
            new_borns = []
            new_born_count = 0
            dead_count = 0
            self.cells[0]['f_max'] = 500
            print ("Animal Count = ", len(self.cells[0]['animals']))
            for y in range(len(self.cells[0]['animals'])):
                animal = self.cells[0]['animals'][y]
                animal.calculate_fitness()
                feed_left = animal.feeds(self.cells[0]['f_max'])
                self.cells[0]['f_max'] =  feed_left
                animal.birth(len(self.cells[0]['animals']))
                baby = animal.procreation()
                if baby is not None:
                    new_borns.append(baby)
                animal.migration()
                animal.comense_aging()
                animal.comense_weight_loss()
                animal.death()
            dead_count = len([animal for animal in self.cells[0]['animals'] if animal.dead])
            self.cells[0]['animals'] = [animal for animal in self.cells[0]['animals'] if not animal.dead]
            if len(new_borns) > 0:
                self.cells[0]['animals'].extend(new_borns)

            print("Dead:", dead_count)
            print("Babies:", len(new_borns))

    def add_population(self):
        """
        Add a population to the island
        :param population: List of dictionaries specifying population
        """
        for i in self.ini_pop:
            animals = i['pop']
            for x in animals:
                if x['species'] == 'Herbivore':
                    obj = Herbivore(x['age'],x['weight'])
                self.cells[0]['animals'].append(obj)

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
