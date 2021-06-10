from .cells import Water, Lowland, Highland, Desert
import random
import matplotlib.pyplot as plt
import numpy as np


class Island:
    def __init__(self, geo):
        self.geo = geo
        self.cell_list = []
        self.plots = [{'Name': 'Geography', 'Plot': None, 'Position': 1},
                      {'Name': 'Number_of_species', 'Plot': None, 'Position': 2},
                      {'Name': 'Herbivore_Distribution', 'Plot': None, 'Position': 3},
                      {'Name': 'Carnivore_Distribution', 'Plot': None, 'Position': 4},
                      {'Name': 'Fitness_Histogram', 'Plot': None, 'Position': 5},
                      {'Name': 'Weight_Histogram', 'Plot': None, 'Position': 6},
                      {'Name': 'Age_Histogram', 'Plot': None, 'Position': 7},
                      ]
        self.add_plots(4,2)
        self.make_map()
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

    def add_plots(self, rows, cols):
        fig = plt.figure()
        for plot in self.plots:
            ax = fig.add_subplot(rows,cols,plot['Position'])
            plot['Plot'] = ax

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
            # print("Cell Location:", cell.loc)
            # print("Total Herbivore In Cell:", len(cell.herbivores))
            # print("Total Carnivore In Cell:", len(cell.carnivores))
            if year_number > 1:
                self.commence_migration(cell)
            herbivores_fitness,carnivores_fitness,herbivores_age,\
                carnivores_age,herbivores_weight,carnivores_weight= cell.cell_annual_lifecycle()
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

    def update_number_of_species_graph(self, current_year, total_years, herbivore_count, carnivores_count):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Number_of_species'][0]
        if current_year == 1:
            ax.set_xlim(0, total_years)
            ax.set_ylim(0, 15000)
            self.line_herbivores = ax.plot(np.arange(total_years),
                                           np.full(total_years, np.nan), 'b-')[0]
            self.line_carnivores = ax.plot(np.arange(total_years),
                                           np.full(total_years, np.nan), 'r-')[0]
        y_data_herbivore = self.line_herbivores.get_ydata()
        y_data_herbivore[current_year - 1] = herbivore_count
        y_data_carnivore = self.line_carnivores.get_ydata()
        y_data_carnivore[current_year - 1] = carnivores_count
        self.line_herbivores.set_ydata(y_data_herbivore)
        self.line_carnivores.set_ydata(y_data_carnivore)
        # ax.pause(1e-6)
        self.show_plots()
        # for n in range(total_years):
        #     y_data = line_herbivores.get_ydata()
        #     y_data[n] = np.random.random()
        #     line.set_ydata(y_data)
        #     plt.pause(1e-6)

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
        return herbivore_dist,carnivore_dist

    def update_system_map(self, herbivore_map, carnivore_map, cmax_animals):
        """Update the 2D-view of the system."""

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

    def fitness_histogram(self, fitness, fitness_distribution):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Fitness_Histogram'][0]
        if fitness == 1:
            bins = int(fitness_distribution['max'] / fitness_distribution['delta'])
            ax.hist(self.fitness_values_herbivores, bins, ec='blue', histtype='step', label='Herbivores')
            ax.hist(self.fitness_values_carnivores, bins, ec='red', histtype='step', label='Carnivores')
        else:
            ax.clear()
            bins = int(fitness_distribution['max'] / fitness_distribution['delta'])
            ax.hist(self.fitness_values_herbivores, bins, ec='blue', histtype='step', label='Herbivores')
            ax.hist(self.fitness_values_carnivores, bins, ec='red', histtype='step', label='Carnivores')

    def age_histogram(self, age, fitness_distribution):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Age_Histogram'][0]
        if age == 1:
            bins = int(fitness_distribution['max'] / fitness_distribution['delta'])
            ax.hist(self.age_values_herbivores, bins, ec='blue', histtype='step', label='Herbivores')
            ax.hist(self.age_values_carnivores, bins, ec='red', histtype='step', label='Carnivores')
        else:
            ax.clear()
            bins = int(fitness_distribution['max'] / fitness_distribution['delta'])
            ax.hist(self.age_values_herbivores, bins, ec='blue', histtype='step', label='Herbivores')
            ax.hist(self.age_values_carnivores, bins, ec='red', histtype='step', label='Carnivores')


    def weight_histogram(self, weight, fitness_distribution):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Weight_Histogram'][0]
        if weight == 1:
            bins = int(fitness_distribution['max'] / fitness_distribution['delta'])
            ax.hist(self.weight_values_herbivores, bins, ec='blue', histtype='step', label='Herbivores')
            ax.hist(self.weight_values_carnivores, bins, ec='red', histtype='step', label='Carnivores')
        else:
            ax.clear()
            bins = int(fitness_distribution['max'] / fitness_distribution['delta'])
            ax.hist(self.weight_values_herbivores, bins, ec='blue', histtype='step', label='Herbivores')
            ax.hist(self.weight_values_carnivores, bins, ec='red', histtype='step', label='Carnivores')



    # def update_system_map(self, herbivores_map,cmax_animals):
    #     """
    #     Update herbivore distribution map.
    #
    #     Parameters
    #     ----------
    #     herbivores_map : list
    #         List of n elements, where n is a number of cells in the map. Elements correspond to
    #         the numbers of herbivores living currently in a given cell.
    #     """
    #     if self._herb_dist_axis is not None:
    #         self._herb_dist_axis.set_data(herbivores_map)
    #     else:
    #         self._herb_dist_axis = self._herb_dist_ax.imshow(herbivores_map,
    #                                                          interpolation='nearest',
    #                                                          vmin=0,
    #                                                          vmax=self.cmax_animals['Herbivore'],
    #                                                          cmap='Greens')
    #         self._herb_dist_ax.set_xticks(range(0, len(self._island_rgb[0]), 2))
    #         self._herb_dist_ax.set_xticklabels(range(1, 1 + len(self._island_rgb[0]), 2))
    #         self._herb_dist_ax.set_yticks(range(0, len(self._island_rgb), 2))
    #         self._herb_dist_ax.set_yticklabels(range(1, 1 + len(self._island_rgb), 2))
    #         plt.colorbar(self._herb_dist_axis, ax=self._herb_dist_ax,
    #                      orientation='vertical')
    # # def setup(self, final_step, img_step):
    #     """
    #     Prepare graphics.
    #
    #     Call this before calling :meth:`update()` for the first time after
    #     the final time step has changed.
    #
    #     :param final_step: last time step to be visualised (upper limit of x-axis)
    #     :param img_step: interval between saving image to file
    #     """
    #     self._img_step = img_step
    #
    #     # create new figure window
    #
    #     # Add left subplot for images created with imshow().
    #     # We cannot create the actual ImageAxis object before we know
    #     # the size of the image, so we delay its creation.
    #     if self._map_ax is None:
    #         self._map_ax = self._fig.add_subplot(1, 2, 1)
    #         self._img_axis = None
    #
    #     # Add right subplot for line graph of mean.
    #     if self._mean_ax is None:
    #         self._mean_ax = self._fig.add_subplot(1, 2, 2)
    #         self._mean_ax.set_ylim(-0.05, 0.05)
    #
    #     # needs updating on subsequent calls to simulate()
    #     # add 1 so we can show values for time zero and time final_step
    #     self._mean_ax.set_xlim(0, final_step + 1)
    #
    #     if self._mean_line is None:
    #         mean_plot = self._mean_ax.plot(np.arange(0, final_step + 1),
    #                                        np.full(final_step + 1, np.nan))
    #         self._mean_line = mean_plot[0]
    #     else:
    #         x_data, y_data = self._mean_line.get_data()
    #         x_new = np.arange(x_data[-1] + 1, final_step + 1)
    #         if len(x_new) > 0:
    #             y_new = np.full(x_new.shape, np.nan)
    #             self._mean_line.set_data(np.hstack((x_data, x_new)),
    #                                      np.hstack((y_data, y_new)))
