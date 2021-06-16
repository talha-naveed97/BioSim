# -*- coding: utf-8 -*-

"""
This module implements the BioSim class that runs the complete simulation.

"""
import random
from .island import Island


class BioSim:
    """
    The BioSim class that sets up and runs the simulation.

    Parameters
    ----------
    island_map : str
        Multi-line string specifying island geography

    ini_pop : list
        List of dictionaries specifying initial population

    seed : int
        Random number seed

    vis_years : int
        Years between visualization updates (if 0, disable graphics)

    ymax_animals : float
        Number specifying y-axis limit for graph showing animal numbers

    cmax_animals : dict
        Specifying color-code limits for animal densities

    hist_specs : dict
        Specifications for histograms, see below

    img_dir : str
        Path to directory for figures

    img_base : str
        Beginning of file name for figures

    img_fmt : str
        File type for figures, e.g. ’png’

    img_years : str
        Years between visualizations saved to files (default: vis_years)
        If 0 then no images will be saved

    log_file : str
        If given, write animal counts to this file


    If **ymax_animals** is None, the y-axis limit should be adjusted automatically.

    If **cmax_animals** is None, sensible, fixed default values should be used. **cmax_animals**
    is a dict mapping species names to numbers, e.g., {’Herbivore’: 50, ’Carnivore’: 20}

    **hist_specs** is a dictionary with one entry per property for which a histogram shall be shown.
    For each property, a dictionary providing the maximum value and the bin width must be
    given, e.g., {'weight': {'max': 80, 'delta': 2}, 'fitness': {'max': 1.0, 'delta': 0.05}}
    Permitted properties are *weight*, *age*, *fitness*.

    If **img_dir** is None, no figures are written to file.
    Filenames are formed as ``f{os.path.join(img_dir, img_base}_{img_number:05d}.{img_fmt}``
    where **img_number** are consecutive image numbers starting from 0.
    **img_dir** and **img_base** must either be both None or both strings.

    """
    default_cmax = {'Herbivore': 200, 'Carnivore': 50}
    default_hist_specs = {'fitness': {'max': 1.0, 'delta': 0.05},
                          'age': {'max': 60.0, 'delta': 2},
                          'weight': {'max': 60, 'delta': 2}}

    def __init__(self, island_map, ini_pop, seed,
                 vis_years=1, ymax_animals=None, cmax_animals=None, hist_specs=None,
                 img_dir=None, img_base=None, img_fmt='png', img_years=None,
                 log_file=None):

        self.ini_pop = ini_pop
        self.seed = seed
        self.num_years = 0
        self.current_year = 0
        self.vis_years = 1
        if cmax_animals is None:
            self.c_max_animal = self.default_cmax
        else:
            self.c_max_animal = cmax_animals

        if hist_specs is None:
            self.hist_specs = self.default_hist_specs
        else:
            self.hist_specs = hist_specs

        self.island = Island(island_map, img_dir=img_dir, img_name=img_base, img_fmt=img_fmt)

        if ini_pop is not None:
            self.add_population(ini_pop)

        self.vis_years = vis_years
        self.y_max_animals = ymax_animals

        if img_years is None:
            self.img_years = self.vis_years
        else:
            self.img_years = img_years

        if self.vis_years > 0:
            if self.img_years % self.vis_years != 0:
                raise ValueError('img_steps must be multiple of vis_steps')

        random.seed(self.seed)

    def set_animal_parameters(self, species, params):
        """
        Set parameters for animal species.

        Parameters
        ----------
        species : str
            Name of animal species

        params : dict
            Dictionary with valid parameter specification for species


        |

        """
        self.island.update_animal_params(species, params)

    def set_landscape_parameters(self, landscape, params):
        """

        Parameters
        ----------
        landscape : str
            Code letter for landscape

        params :  dict
            Dictrionary with valid parameter specification for landscape


        |
        """
        self.island.update_cell_params(landscape, params)

    def simulate(self, num_years):
        """
        Run simulation while visualizing the result.

        Parameters
        ----------
        num_years : int
            Number of years to simulate


        |
        """
        if self.num_years == 0:
            self.num_years = num_years
        else:
            self.num_years += num_years

        if self.vis_years > 0:
            if self.current_year == 0:
                self.island.setup_visualization(self.num_years, self.c_max_animal,
                                                self.hist_specs, self.y_max_animals, self.img_years)

        herbivore_count = []
        carnivore_count = []
        for x in range(self.current_year, self.num_years):
            self.current_year = x + 1
            self.island.commence_annual_cycle()
            animal_counts = self.num_animals_per_species
            if self.vis_years > 0 and self.current_year % self.vis_years == 0:
                self.island.update_visualization(self.current_year, self.num_years,
                                                 animal_counts,
                                                 self.c_max_animal, self.hist_specs,
                                                 self.y_max_animals)

            herbivore_count.append(counts['Herbivore'])
            carnivore_count.append(counts['Carnivore'])

        return herbivore_count, carnivore_count

    def add_population(self, population):
        """
        Add a population to the island

        Parameters
        ----------
        population : dict
            List of dictionaries specifying population


        |

        """
        self.island.add_population(population)

    @property
    def year(self):
        """
        Last year simulated.


        |

        """
        return self.current_year

    @property
    def num_animals(self):
        """
        Total number of animals on island.


        |

        """
        return self.island.get_total_animal_count()

    @property
    def num_animals_per_species(self):
        """
        Number of animals per species in island, as dictionary.


        |

        """
        return self.island.get_total_species_count()

    def make_movie(self, movie_format=None):
        """
        Create MPEG4 movie from visualization images saved.


        |

        """
        self.island.make_movie(movie_format)
