from .cells import Water, Lowland, Highland, Desert
import random
import matplotlib.pyplot as plt
import numpy as np


class Island:
    def __init__(self, geo):
        self.geo = geo
        self.cell_list = []
        self.plots = [{'Name': 'Geography', 'Plot': None},
                      {'Name': 'Number_of_species', 'Plot': None}
                      ]
        self.add_plots()
        self.make_map()
        self.line_herbivores = []
        self.line_carnivores = []

    def add_plots(self):
        index = 1
        fig = plt.figure()
        for plot in self.plots:
            ax = fig.add_subplot(2, 2, index)
            plot['Plot'] = ax
            index += 1

    def make_map(self):
        map_list = self.geo.splitlines()
        rows = len(map_list)
        map_rgb = []
        for x in range(1, rows + 1):
            rgb_cells_in_row = []
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
                rgb_cells_in_row.append(cell.rgb)
                self.cell_list.append(cell)
            map_rgb.append(rgb_cells_in_row)

        # fig = plt.figure()
        # ax1 = fig.add_subplot(2, 2, 1)
        # ax2 = fig.add_subplot(2, 2, 2)
        # #ax1 = fig.add_axes([0.1, 0.1, 0.7, 0.8])  # llx, lly, w, h
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Geography'][0]
        ax.imshow(map_rgb)
        ax.set_xticks(range(len(map_rgb[0])))
        ax.set_xticklabels(range(1, 1 + len(map_rgb[0])))
        ax.set_yticks(range(len(map_rgb)))
        ax.set_yticklabels(range(1, 1 + len(map_rgb)))
        self.show_plots()

    def add_population(self, species):
        for record in species:
            loc = record['loc']
            animals = record['pop']
            cell = [item for item in self.cell_list if item.loc[0] == loc[0] and item.loc[1] == loc[1]][0]
            cell.add_animal(animals)

    def commence_annual_cycle(self, year_number):
        for cell in self.cell_list:
            #print("Cell Location:", cell.loc)
            #print("Total Herbivore In Cell:", len(cell.herbivores))
            #print("Total Carnivore In Cell:", len(cell.carnivores))
            if year_number > 1:
                self.commence_migration(cell)
            cell.cell_annual_lifecycle()
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
                    else:
                        migrating_cell.carnivores.append(animal)

    def get_random_cell(self, possibilies):
        return random.choice(possibilies)

    def show_plots(self):
        plt.pause(1e-6)
        plt.show(block=False)

    def get_total_species_count(self):
        total_herbivores = sum(len(c.herbivores) for c in self.cell_list)
        total_carnivores = sum(len(c.carnivores) for c in self.cell_list)
        return total_herbivores, total_carnivores

    def update_number_of_species_graph(self,current_year,total_years,herbivore_count,carnivores_count):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Number_of_species'][0]
        if current_year == 1:
            ax.set_xlim(0, total_years)
            ax.set_ylim(0, 5000)
            self.line_herbivores = ax.plot(np.arange(total_years),
                       np.full(total_years, np.nan), 'b-')[0]
            self.line_carnivores = ax.plot(np.arange(total_years),
                                           np.full(total_years, np.nan), 'r-')[0]
        y_data_herbivore = self.line_herbivores.get_ydata()
        y_data_herbivore[current_year-1] = herbivore_count
        y_data_carnivore = self.line_carnivores.get_ydata()
        y_data_carnivore[current_year - 1] = carnivores_count
        self.line_herbivores.set_ydata(y_data_herbivore)
        self.line_carnivores.set_ydata(y_data_carnivore)
        #ax.pause(1e-6)
        self.show_plots()
        # for n in range(total_years):
        #     y_data = line_herbivores.get_ydata()
        #     y_data[n] = np.random.random()
        #     line.set_ydata(y_data)
        #     plt.pause(1e-6)
