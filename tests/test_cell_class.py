# -*- coding: utf-8 -*-

"""
Test set for Cells class for INF200 June 2021.
"""

import pytest
from src.biosim import cells


class TestCellClass:

    @pytest.fixture(autouse=True)
    def cell_for_testing(self):
        """
        Initialize cell types for tests.
        """
        self.water = cells.Water((1, 1))
        self.desert = cells.Desert((5, 5))
        self.highland = cells.Highland((10, 5))
        self.lowland = cells.Lowland((6, 12))

    def test_water_not_accessible(self):
        """
        Test that water cell does not allow animals to enter.
        """
        assert self.water.allows_animal is False

    def test_desert_is_accessible(self):
        """
        Test that desert cell allows animals to enter.
        """
        assert self.desert.allows_animal is True

    def test_highland_is_accessible(self):
        """
        Test that highland cell allows animals to enter.
        """
        assert self.highland.allows_animal is True

    def test_lowland_is_accessible(self):
        """
        Test that lowland cell allows animals to enter.
        """
        assert self.lowland.allows_animal is True

    def test_water_has_no_fodder(self):
        """
        Test that water cell has no fodder.
        """
        assert self.water.f_max == 0

    def test_desert_has_no_fodder(self):
        """
        Test that desert cell has no fodder.
        """
        assert self.desert.f_max == 0

    @staticmethod
    def test_update_defaults():
        """
        Test that default parameters of cells are updated correctly.
        """
        cells.Highland.update_defaults({'f_max': 10.})
        assert cells.Highland.f_max == 10.

    def test_fodder_reset(self):
        """
        Test that amount of fodder is correctly reset to f_max.
        """
        self.lowland.food_status = 5.
        self.lowland.reset_cell()
        assert self.lowland.food_status == self.lowland.f_max

    def test_add_animal(self):
        """
        Test that animals are added correctly in corresponding lists.
        """
        herb = [{'species': 'Herbivore', 'age': 1, 'weight': 10} for _ in range(5)]
        carn = [{'species': 'Carnivore', 'age': 2, 'weight': 5} for _ in range(7)]
        self.lowland.add_animal(herb)
        self.lowland.add_animal(carn)
        assert len(self.lowland.herbivores) == 5
        assert len(self.lowland.carnivores) == 7

    def test_loc_correctly_specified(self):
        """
        Test that cell locations correctly specified.
        """
        assert self.water.loc == (1, 1)
        assert self.desert.loc == (5, 5)
        assert self.highland.loc == (10, 5)
        assert self.lowland.loc == (6, 12)

    def test_total_migration_cells(self):
        """
        Test that number of migrations cells relative to the current cell are equal to 4.
        """
        migration_cells = self.lowland.get_migration_possibilities()
        assert len(migration_cells) == 4

    def test_no_diagonal_migration(self):
        """
        Test that migrations cells are not diagonal.
        """
        migration_cells = self.lowland.get_migration_possibilities()
        diagonal_cells = [(5, 11), (5, 13), (7, 11), (7, 13)]
        common_cells = set(migration_cells).intersection(diagonal_cells)
        assert common_cells == set([])

    def test_correct_migration_cells(self):
        """
        Test that relative locations of migrations cells are correct.
        """
        migration_cells = self.lowland.get_migration_possibilities()
        correct_cells = [(6, 11), (6, 13), (5, 12), (7, 12)]
        assert set(migration_cells) == set(correct_cells)

    @staticmethod
    def test_set_cell_params_keys():
        """
        Test that errors are raised in case of incorrect keys in set_cell_params.
        """
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
        """
        Test that errors are raised in case of incorrect values in set_cell_params.
        """
        with pytest.raises(ValueError):
            cells.set_cell_params('L', {'f_max': -10})

        with pytest.raises(ValueError):
            cells.set_cell_params('L', {'f_max': 'string'})
