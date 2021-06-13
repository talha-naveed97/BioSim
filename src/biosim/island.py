from .cells import Water, Lowland, Highland, Desert, set_cell_params, update_animal_params
import random
from .graphics import Graphics


class Island:
    def __init__(self, geo, img_dir=None, img_name=None, img_fmt=None):
        self.geo = geo
        self.map_rgb = []
        self.cell_list = []
        self.add_cells()
        self.graphics =  Graphics(img_dir, img_name, img_fmt)
        self.fitness_values_herbivores = []
        self.fitness_values_carnivores = []
        self.age_values_herbivores = []
        self.age_values_carnivores = []
        self.weight_values_herbivores = []
        self.weight_values_carnivores = []

    def add_cells(self):
        map_list = self.geo.splitlines()
        rows = len(map_list)
        for row in range(1, rows + 1):
            rgb_cells_in_row = []
            line = map_list[row - 1].strip()
            chars = len(line)
            if row > 1 and chars != len(map_list[row - 2]):
                raise ValueError('Inconsistent row length')
            cell = None
            for col in range(1, chars + 1):
                land_type = line[col - 1]
                if (row == 1 or row == rows or col == 1 or col == chars) \
                        and land_type != 'W':
                    raise ValueError('Cannot have non ocean boundry')
                loc = (row, col)
                if land_type == 'W':
                    cell = Water(loc)
                elif land_type == 'H':
                    cell = Highland(loc)
                elif land_type == 'L':
                    cell = Lowland(loc)
                elif land_type == 'D':
                    cell = Desert(loc)
                else:
                    raise ValueError('Cannot Identify Land Type')
                rgb_cells_in_row.append(cell.rgb)
                self.cell_list.append(cell)
            self.map_rgb.append(rgb_cells_in_row)

    def update_cell_params(self, landscape, params):
        set_cell_params(landscape, params)

    def update_animal_params(self, species, params):
        update_animal_params(species, params)

    def add_population(self, species):
        for record in species:
            loc = record['loc']
            animals = record['pop']
            cell = [item for item in self.cell_list if item.loc[0] == loc[0] and item.loc[1] == loc[1]][0]
            cell.add_animal(animals)

    def commence_annual_cycle(self, year_number):
        self.fitness_values_herbivores = []
        self.fitness_values_carnivores = []
        self.age_values_herbivores = []
        self.age_values_carnivores = []
        self.weight_values_herbivores = []
        self.weight_values_carnivores = []
        for cell in self.cell_list:
            if not cell.allows_animal:
                continue
            if year_number > 1:
                self.commence_migration(cell)
            herbivores_fitness, carnivores_fitness, herbivores_age, \
            carnivores_age, herbivores_weight, carnivores_weight = cell.cell_annual_lifecycle()
            self.fitness_values_herbivores.extend(herbivores_fitness)
            self.fitness_values_carnivores.extend(carnivores_fitness)
            self.age_values_herbivores.extend(herbivores_age)
            self.age_values_carnivores.extend(carnivores_age)
            self.weight_values_herbivores.extend(herbivores_weight)
            self.weight_values_carnivores.extend(carnivores_weight)
            cell.reset_cell()

    def commence_migration(self, cell):
        animals_for_migration = [animal for animal in cell.herbivores + cell.carnivores if
                                 animal.migrates]
        if len(animals_for_migration) > 0:
            migration_possibilies = cell.get_migration_possibilities()
            for animal in animals_for_migration:
                migrating_to = self.get_random_cell(migration_possibilies)
                migrating_cell = [cl for cl in self.cell_list
                                  if cl.loc[0] == migrating_to[0] and cl.loc[1] == migrating_to[1]][0]
                if migrating_cell.allows_animal:
                    if animal.__class__.__name__ == 'Herbivore':
                        migrating_cell.herbivores.append(animal)
                        index = cell.herbivores.index(animal)
                        cell.herbivores.pop(index)
                    else:
                        migrating_cell.carnivores.append(animal)
                        index = cell.carnivores.index(animal)
                        cell.carnivores.pop(index)

    def get_random_cell(self, possibilities):
        _dir = random.randint(0, 3)
        return possibilities[_dir]

    def get_total_species_count(self):
        total_herbivores = sum(len(c.herbivores) for c in self.cell_list)
        total_carnivores = sum(len(c.carnivores) for c in self.cell_list)
        return {'Herbivore': total_herbivores, 'Carnivore': total_carnivores}

    def get_total_animal_count(self):
        total_animals = sum(len(c.herbivores) + len(c.carnivores) for c in self.cell_list)
        return total_animals

    def setup_visualization(self,rows, cols, total_years, cmap, hist_specs, y_max, img_years):
        herb_dist, carn_dist = self.get_distributions()
        self.graphics.setup_visualization(rows, cols, total_years, cmap, hist_specs, y_max, img_years,self.map_rgb,
                                          herb_dist, carn_dist)

    def update_visualization(self,year, total_years, herbivore_count, carnivores_count, cmax_animals, hist_specs, y_max):
        herbivore_dist,carnivore_dist = self.get_distributions()
        herbivore_date = {
            "count": herbivore_count,
            "fitness": self.fitness_values_herbivores,
            "age": self.age_values_herbivores,
            "weight": self.weight_values_herbivores,
            "distribution": herbivore_dist
        }

        carnivore_date = {
            "count": carnivores_count,
            "fitness": self.fitness_values_carnivores,
            "age": self.age_values_carnivores,
            "weight": self.weight_values_carnivores,
            "distribution": carnivore_dist
        }
        self.graphics.update_visualization(year, total_years,cmax_animals, hist_specs, y_max,
                                           herbivore_date, carnivore_date)

    def get_distributions(self):
        map_list = self.geo.splitlines()
        rows = len(map_list)
        herbivore_dist = []
        carnivore_dist = []
        for x in range(rows):
            row_list_carnivore = []
            row_list_herbivore = []
            line = map_list[x].strip()
            chars = len(line)
            for y in range(chars):
                loc = (x + 1, y + 1)
                cell = [item for item in self.cell_list if item.loc[0] == loc[0] and item.loc[1] == loc[1]][0]
                row_list_herbivore.append(len(cell.herbivores))
                row_list_carnivore.append(len(cell.carnivores))
            herbivore_dist.append(row_list_herbivore)
            carnivore_dist.append(row_list_carnivore)
        return herbivore_dist, carnivore_dist

    def make_movie(self):
        self.graphics.make_movie()