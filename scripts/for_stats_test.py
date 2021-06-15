import random
from biosim.simulation import BioSim
import textwrap
from scipy import stats

geogr = """\
           WWW
           WLW
           WWW"""

geogr = textwrap.dedent(geogr)

ini_herbs = [{'loc': (2, 2),
              'pop': [{'species': 'Herbivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(50)]}]

distribution = []
for seed in range(10, 15):
    sim = BioSim(geogr, ini_herbs, seed=seed, vis_years=0)
    herbivores, carnivores = sim.simulate(50)
    distribution.append(herbivores)


list1, list2 = random.sample(distribution, 2)
print(stats.ttest_ind(list1, list2))
