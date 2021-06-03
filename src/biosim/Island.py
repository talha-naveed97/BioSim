from .Cells import Water, Lowland, Highland, Desert


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

    def commence_annual_cycle(self):
        for cell in self.cell_list:
            print("Cell Location:",cell.loc)
            print("Total Herbivore In Cell:",len(cell.herbivores))
            print("Total Carnivore In Cell:", len(cell.herbivores))
            cell.cell_annual_lifecycle()
            cell.reset_cell()

