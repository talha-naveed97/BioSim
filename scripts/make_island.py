# -*- coding: utf-8 -*-

import textwrap
from src.biosim.BioSim import BioSim

geogr = """WWW
           WLW
           WWW"""

geogr = textwrap.dedent(geogr)

ini_herbs = [{'loc': (2, 2),
              'pop': [{'species': 'Herbivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(30)]}]

sim = BioSim(island_map = geogr, ini_pop = ini_herbs, seed=100)

sim.set_animal_parameters('Herbivore', {'zeta': 3.5, 'xi': 1.2})

sim.add_population()

sim.simulate(100)
