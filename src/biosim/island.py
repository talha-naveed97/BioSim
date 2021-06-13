from .cells import Water, Lowland, Highland, Desert
import random
import matplotlib.pyplot as plt
import numpy as np


class Island:
    def __init__(self, geo):
        self.geo = geo
        self.map_rgb = []
        self.cell_list = []
        self.add_cells()
        self.plots = [{'Name': 'Geography', 'Plot': None, 'Position': 1},
                      {'Name': 'Number_of_species', 'Plot': None, 'Position': 3},
                      {'Name': 'Herbivore_Distribution', 'Plot': None, 'Position': 4},
                      {'Name': 'Carnivore_Distribution', 'Plot': None, 'Position': 6},
                      {'Name': 'Fitness_Histogram', 'Plot': None, 'Position': 7},
                      {'Name': 'Weight_Histogram', 'Plot': None, 'Position': 8},
                      {'Name': 'Age_Histogram', 'Plot': None, 'Position': 9},
                      ]
        self.line_herbivores = []
        self.line_carnivores = []
        self.herb_dist_axis = None
        self.carn_dist_axis = None
        self.fitness_values_herbivores = []
        self.fitness_values_carnivores = []
        self.age_values_herbivores = []
        self.age_values_carnivores = []
        self.weight_values_herbivores = []
        self.weight_values_carnivores = []
        self.max_species_count = 1000
        self.year_counter = None
        self.year_txt = None
        self.year_template = 'Year: {:5d}'
        self.fig = None

    def setup_visualization(self, rows, cols, total_years, cmap, hist_specs):
        self.fig = plt.figure()
        for plot in self.plots:
            ax = self.fig.add_subplot(rows, cols, plot['Position'])
            plot['Plot'] = ax
        self.make_map()
        self.update_number_of_species_graph(True, 0, total_years, 0, 0)
        self.update_distribution_map(cmap)
        self.update_fitness_histogram(hist_specs['fitness'])
        self.update_weight_histogram(hist_specs['weight'])
        self.update_age_histogram(hist_specs['age'])
        self.year_counter = self.fig.add_axes([0.4, 0.8, 0.2, 0.2])  # llx, lly, w, h
        self.year_counter.axis('off')  # turn off coordinate system
        self.year_txt = self.year_counter.text(0.5, 0.5, self.year_template.format(0),
               horizontalalignment='center',
               verticalalignment='center',
               transform=self.year_counter.transAxes)
        self.show_plots()

    def add_cells(self):
        map_list = self.geo.splitlines()
        rows = len(map_list)
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
            self.map_rgb.append(rgb_cells_in_row)

        # fig = plt.figure()
        # ax1 = fig.add_subplot(2, 2, 1)
        # ax2 = fig.add_subplot(2, 2, 2)
        # #ax1 = fig.add_axes([0.1, 0.1, 0.7, 0.8])  # llx, lly, w, h

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
            # print("Cell Location:", cell.loc)
            # print("Total Herbivore In Cell:", len(cell.herbivores))
            # print("Total Carnivore In Cell:", len(cell.carnivores))
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


    def get_random_cell(self, possibilies):
        _dir = random.randint(0, 3)
        return possibilies[_dir]

    def make_map(self):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Geography'][0]
        ax.imshow(self.map_rgb)
        ax.set_xticks(range(len(self.map_rgb[0])))
        ax.set_xticklabels(range(1, 1 + len(self.map_rgb[0])))
        ax.set_yticks(range(len(self.map_rgb)))
        ax.set_yticklabels(range(1, 1 + len(self.map_rgb)))

    def show_plots(self):
        #plt.show(block=False)
        self.fig.canvas.flush_events()
        plt.pause(1e-6)

    def get_total_species_count(self):
        total_herbivores = sum(len(c.herbivores) for c in self.cell_list)
        total_carnivores = sum(len(c.carnivores) for c in self.cell_list)
        return total_herbivores, total_carnivores

    def update_number_of_species_graph(self, is_init, current_year, total_years, herbivore_count, carnivores_count):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Number_of_species'][0]
        max_count = max(herbivore_count,carnivores_count)
        if is_init:
            ax.set_xlim(0, total_years)
            ax.set_ylim(0, self.max_species_count)
            self.line_herbivores = ax.plot(np.arange(total_years),
                                           np.full(total_years, np.nan), 'b-')[0]
            self.line_carnivores = ax.plot(np.arange(total_years),
                                           np.full(total_years, np.nan), 'r-')[0]
        else:
            # if total_years > len(self.line_herbivores.get_xdata()):
            #     y_data_herbivore = self.line_herbivores.get_ydata()
            #     self.line_herbivores =ax.plot(np.arange(total_years),
            #                                np.full(total_years, np.nan), 'b-')[0]
            #     y_data_carnivore = self.line_carnivores.get_ydata()
            #     self.line_carnivores = ax.plot(np.arange(total_years),
            #                                    np.full(total_years, np.nan), 'b-')[0]
            if total_years > len(self.line_herbivores.get_xdata()):
                x_data_h, y_data_h = self.line_herbivores.get_data()
                x_data_c, y_data_c = self.line_carnivores.get_data()
                x_new_h = np.arange(x_data_h[-1] + 1, total_years + 1)
                x_new_c = np.arange(x_data_c[-1] + 1, total_years + 1)
                ax.set_xlim(0, total_years + 1)
                if len(x_new_h) > 0:
                    y_new_h = np.full(x_new_h.shape, np.nan)
                    self.line_herbivores.set_data(np.hstack((x_data_h, x_new_h)),
                                             np.hstack((y_data_h, y_new_h)))
                if len(x_new_c) > 0:
                    y_new_c = np.full(x_new_c.shape, np.nan)
                    self.line_carnivores.set_data(np.hstack((x_data_c, x_new_c)),
                                             np.hstack((y_data_c, y_new_c)))
            y_val = max(herbivore_count, carnivores_count)
            if self.max_species_count < max_count:
                self.max_species_count = int(1.2 * max_count)
                ax.set_ylim(0, self.max_species_count)
        y_data_herbivore = self.line_herbivores.get_ydata()
        y_data_herbivore[current_year - 1] = herbivore_count
        y_data_carnivore = self.line_carnivores.get_ydata()
        y_data_carnivore[current_year - 1] = carnivores_count
        self.line_herbivores.set_ydata(y_data_herbivore)
        self.line_carnivores.set_ydata(y_data_carnivore)
        self.show_plots()

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

    def update_distribution_map(self, cmax_animals):
        herbivore_map, carnivore_map = self.get_distributions()
        if self.herb_dist_axis is not None:
            self.herb_dist_axis.set_data(herbivore_map)
        else:
            ax_herb = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Herbivore_Distribution'][0]
            self.herb_dist_axis = ax_herb.imshow(herbivore_map,
                                                 interpolation='nearest',
                                                 vmin=-0.25, vmax=cmax_animals['Herbivore'],
                                                 )
            plt.colorbar(self.herb_dist_axis, ax=ax_herb,
                         orientation='vertical')

        if self.carn_dist_axis is not None:
            self.carn_dist_axis.set_data(carnivore_map)
        else:
            ax_carn = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Carnivore_Distribution'][0]
            self.carn_dist_axis = ax_carn.imshow(carnivore_map,
                                                 interpolation='nearest',
                                                 vmin=-0.25, vmax=cmax_animals['Carnivore'],
                                                 )
            plt.colorbar(self.carn_dist_axis, ax=ax_carn,
                         orientation='vertical')

    def update_fitness_histogram(self, fitness_hist_specs):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Fitness_Histogram'][0]
        ax.clear()
        ax.set_title('Fitness histogram',
                     verticalalignment='bottom')
        bins = int(fitness_hist_specs['max'] / fitness_hist_specs['delta'])
        ax.hist((self.fitness_values_herbivores, self.fitness_values_carnivores), bins,
                (0, fitness_hist_specs['max']), histtype='step', linewidth=3,
                label=('Herbivores', 'Carnivores'), color=('g', 'r'))
        ax.legend()

    def update_age_histogram(self, age_hist_specs):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Age_Histogram'][0]
        ax.clear()
        ax.set_title('Age histogram',
                     verticalalignment='bottom')
        bins = int(age_hist_specs['max'] / age_hist_specs['delta'])
        ax.hist((self.age_values_herbivores, self.age_values_carnivores), bins,
                (0, age_hist_specs['max']), histtype='step', linewidth=3,
                label=('Herbivores', 'Carnivores'), color=('g', 'r'))
        ax.legend()

    def update_weight_histogram(self, weight_hist_specs):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Weight_Histogram'][0]
        ax.clear()
        ax.set_title('Weight histogram',
                     verticalalignment='bottom')
        bins = int(weight_hist_specs['max'] / weight_hist_specs['delta'])
        ax.hist((self.weight_values_herbivores, self.weight_values_carnivores), bins,
                (0, weight_hist_specs['max']), histtype='step', linewidth=3,
                label=('Herbivores', 'Carnivores'), color=('g', 'r'))
        ax.legend()

    def update_visualiztion(self, year, total_years, herbivore_count, carnivores_count, cmax_animals, hist_specs):
        self.update_number_of_species_graph(False, year, total_years, herbivore_count, carnivores_count)
        self.update_distribution_map(cmax_animals)
        self.update_fitness_histogram(hist_specs['fitness'])
        self.update_weight_histogram(hist_specs['weight'])
        self.update_age_histogram(hist_specs['age'])
        self.year_txt.set_text(self.year_template.format(year))

