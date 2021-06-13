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
        self.lowland = cells.Lowland((6, 12))

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
        assert self.desert.f_max == 0

    @staticmethod
    def test_update_defaults():
        cells.Highland.update_defaults({'f_max': 10.})
        assert cells.Highland.f_max == 10.

    def test_fodder_reset(self):
        self.lowland.food_status = 5.
        self.lowland.reset_cell()
        assert self.lowland.food_status == self.lowland.f_max

    def test_add_animal(self):
        herb = [{'species': 'Herbivore', 'age': 1, 'weight': 10} for _ in range(5)]
        carn = [{'species': 'Carnivore', 'age': 2, 'weight': 5} for _ in range(7)]
        self.lowland.add_animal(herb)
        self.lowland.add_animal(carn)
        assert len(self.lowland.herbivores) == 5
        assert len(self.lowland.carnivores) == 7

    def test_loc_correctly_specified(self):
        assert self.water.loc == (1, 1)
        assert self.desert.loc == (5, 5)
        assert self.highland.loc == (10, 5)
        assert self.lowland.loc == (6, 12)

    def test_total_migration_cells(self):
        migration_cells = self.lowland.get_migration_possibilities()
        assert len(migration_cells) == 4

    def test_no_diagonal_migration(self):
        migration_cells = self.lowland.get_migration_possibilities()
        diagonal_cells = [(5, 11), (5, 13), (7, 11), (7, 13)]
        common_cells = set(migration_cells).intersection(diagonal_cells)
        assert common_cells == set([])

    def test_correct_migration_cells(self):
        migration_cells = self.lowland.get_migration_possibilities()
        correct_cells = [(6, 11), (6, 13), (5, 12), (7, 12)]
        assert set(migration_cells) == set(correct_cells)

    @staticmethod
    def test_set_cell_params_keys():
        with pytest.raises(KeyError):
            cells.set_cell_params('wrong_land_key', {'f_max': 10.})

        with pytest.raises(KeyError):
            cells.set_cell_params('H', {'wrong_params_key': 10.})

        with pytest.raises(KeyError):
            cells.set_cell_params('D', {'f_max': 10.})

        with pytest.raises(KeyError):
            cells.set_cell_params('W', {'f_max': 10.})


    @staticmethod
    def test_set_cell_params_values():
        with pytest.raises(ValueError):
            cells.set_cell_params('L', {'f_max': -10})

        with pytest.raises(ValueError):
            cells.set_cell_params('L', {'f_max': 'string'})