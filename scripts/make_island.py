# -*- coding: utf-8 -*-

import textwrap
from src.biosim.BioSim import BioSim

geogr = """WWWWW
WWLHW
WDDLW
WWWWW
"""

geogr = textwrap.dedent(geogr)
#
# island = Island(geogr)
#
# island.make_map()

ini_herbs = [{'loc': (2, 3),
              'pop': [{'species': 'Herbivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(150)]}]
ini_carns = [{'loc': (2, 3),
              'pop': [{'species': 'Carnivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(40)]}]

sim = BioSim(island_map=geogr, ini_pop=ini_herbs + ini_carns, seed=12)

sim.set_animal_parameters('Herbivore', {'zeta': 3.5, 'xi': 1.2})

sim.set_animal_parameters('Carnivore', {'a_half': 70, 'phi_age': 0.5,
                                        'omega': 0.3, 'F': 65,
                                        'DeltaPhiMax': 9.})

sim.set_landscape_parameters('L', {'f_max': 800})

sim.add_population(ini_herbs + ini_carns)

sim.simulate(100)
