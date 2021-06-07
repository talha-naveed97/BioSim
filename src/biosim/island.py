from .cells import Water, Lowland, Highland, Desert
import random

class Island:
    def __init__(self, geo):
        self.geo = geo
        self.cell_list = []
        self.make_map()

    def make_map(self):
        map_list = self.geo.splitlines()
        rows = len(map_list)
        for x in range(1, rows + 1):
            line = map_list[x - 1].strip()
            chars = len(line)
            cell = None
            for y in range(1, chars + 1):
                land_type = line[y - 1]
                loc = (x, y)
                if land_type == 'W':
                    cell = Water(loc)
                elif land_type == 'H':
                    cell = Highland(loc)
                elif land_type == 'L':
                    cell = Lowland(loc)
                elif land_type == 'D':
                    cell = Desert(loc)
                self.cell_list.append(cell)

    def add_population(self,species):
        for record in species:
            loc = record['loc']
            animals = record['pop']
            cell = [item for item in self.cell_list if item.loc[0] == loc[0] and item.loc[1] == loc[1]][0]
            cell.add_animal(animals)

    def commence_annual_cycle(self,year_number):
        for cell in self.cell_list:
            print("Cell Location:", cell.loc)
            print("Total Herbivore In Cell:", len(cell.herbivores))
            print("Total Carnivore In Cell:", len(cell.carnivores))
            if year_number > 1:
                self.commence_migration(cell)
            cell.cell_annual_lifecycle()
            cell.reset_cell()

    def commence_migration(self,cell):
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
                    else:
                        migrating_cell.carnivores.append(animal)

    def get_random_cell(self,possibilies):
        return random.choice(possibilies)
