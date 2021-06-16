# -*- coding: utf-8 -*-

"""
Statisitical tests for BioSim, INF200 June 2021.
"""

from biosim.simulation import BioSim
import textwrap
from scipy import stats
import pytest
import random


class TestStatistical:

    @pytest.fixture(autouse=True)
    def geo_for_test(self):
        """
        Initialize a single cell geography and herbivores and carnivores for testing.
        """
        self.geogr = """\
                        WWW
                        WLW
                        WWW"""
        self.geogr = textwrap.dedent(self.geogr)
        self.ini_herbs = [{'loc': (2, 2),
                           'pop': [{'species': 'Herbivore',
                                    'age': 5,
                                    'weight': 20}
                                   for _ in range(50)]}]

        self.ini_carns = [{'loc': (2, 2),
                           'pop': [{'species': 'Carnivore',
                                    'age': 5,
                                    'weight': 20}
                                   for _ in range(20)]}]

    def test_herbivore_ttest(self):
        """
        Test for the null hypothesis that average number of herbivores are
        identical in two independent single-cell, no migration simulations.
        """
        samples = []
        for seed in range(1, 20):
            sim = BioSim(self.geogr, self.ini_herbs, seed=seed, vis_years=0)
            herbivores, carnivores = sim.simulate(100)
            samples.append(herbivores)

        sample1, sample2 = random.sample(samples, 2)
        assert stats.ttest_ind(sample1, sample2).pvalue > 0.05

    def test_carn_ttest_without_feeding(self):
        """
        Test for the null hypothesis that average number of carnivores (when there are
        no herbivores to prey on) in two independent single-cell, no migration simulations.
        """

        samples = []
        for seed in range(1, 20):
            sim = BioSim(self.geogr, self.ini_carns, seed=seed, vis_years=0)
            herbivores, carnivores = sim.simulate(100)
            samples.append(carnivores)

        sample1, sample2 = random.sample(samples, 2)
        assert stats.ttest_ind(sample1, sample2).pvalue > 0.05

    def test_carn_ttest_with_feeding(self):
        """
        Test for the null hypothesis that average number of carnivores (when there are
        herbivores to prey on) in two independent single-cell, no migration simulations.
        """
        samples_herbivores = []
        samples_carnivores = []
        for seed in range(1, 20):
            sim = BioSim(self.geogr, self.ini_herbs, seed=seed, vis_years=0)
            sim.simulate(50)
            sim.add_population(self.ini_carns)
            herbivores, carnivores = sim.simulate(100)
            samples_herbivores.append(herbivores)
            samples_carnivores.append(carnivores)

        sample1, sample2 = random.sample(samples_carnivores, 2)
        assert stats.ttest_ind(sample1, sample2).pvalue > 0.05
