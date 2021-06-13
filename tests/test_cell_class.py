# -*- coding: utf-8 -*-

"""
Test set for Cells class for INF200 June 2021.
"""

import pytest
from src.biosim import cells


class TestCellClass:

    @pytest.fixture(autouse=True)
    def cell_for_testing(self):
        self.water = cells.Water((1, 1))
        self.desert = cells.Desert((5, 5))
        self.highland = cells.Highland((10, 5))
        self.lowland = cells.Lowland((10, 12))

    def test_water_not_accessible(self):
        assert self.water.allows_animal is False

    def test_desert_is_accessible(self):
        assert self.desert.allows_animal is True

    def test_highland_is_accessible(self):
        assert self.highland.allows_animal is True

    def test_lowland_is_accessible(self):
        assert self.lowland.allows_animal is True

    def test_water_has_no_fodder(self):
        assert self.water.f_max == 0

    def test_desert_has_no_fodder(self):
        assert self.water.f_max == 0

    @staticmethod
    def test_update_defaults():
        cells.Highland.update_defaults({'f_max': 10.})
        assert cells.Highland.f_max == 10.

    def test_add_animal(self):
        herb = [{'species': 'Herbivore', 'age': 1, 'weight': 10} for _ in range(5)]
        carn = [{'species': 'Carnivore', 'age': 2, 'weight': 5} for _ in range(7)]
        self.lowland.add_animal(herb)
        self.lowland.add_animal(carn)
        assert len(self.lowland.herbivores) == 5
        assert len(self.lowland.carnivores) == 7
