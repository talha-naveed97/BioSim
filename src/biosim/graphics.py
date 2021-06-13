import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess

# If you installed ffmpeg using conda or installed both softwares in
# standard ways on your computer, no changes should be required.
_FFMPEG_BINARY = 'ffmpeg'
_MAGICK_BINARY = 'magick'

# update this to the directory and file-name beginning
# for the graphics files
_DEFAULT_GRAPHICS_DIR = os.path.join('..', 'data')
_DEFAULT_GRAPHICS_NAME = 'dv'
_DEFAULT_IMG_FORMAT = 'png'
_DEFAULT_MOVIE_FORMAT = 'mp4'   # alternatives: mp4, gif

class Graphics:
    def __init__(self, img_dir=None, img_name=None, img_fmt=None):
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
        self.max_species_count = 1000
        self.year_counter = None
        self.year_txt = None
        self.year_template = 'Year: {:5d}'
        self.fig = None
        self.img_dir = img_dir

        if self.img_dir is None:
            self.img_dir = _DEFAULT_GRAPHICS_DIR
        if img_name is None:
            img_name = _DEFAULT_GRAPHICS_NAME

        if self.img_dir is not None:
            self._img_base = os.path.join(self.img_dir, img_name)
        else:
            self._img_base = None

        self._img_fmt = img_fmt if img_fmt is not None else _DEFAULT_IMG_FORMAT

        self._img_ctr = 0
        self.img_years = 1

    def show_plots(self):
        self.fig.canvas.flush_events()
        plt.pause(1e-6)

    def setup_visualization(self, rows, cols, total_years, cmap, hist_specs, y_max, img_years,map_rgb, herb_dist,carn_dist):
        self.fig = plt.figure()
        for plot in self.plots:
            ax = self.fig.add_subplot(rows, cols, plot['Position'])
            plot['Plot'] = ax
        self.make_map(map_rgb)
        self.update_number_of_species_graph(True, 0, total_years, 0, 0, y_max)
        self.update_distribution_map(herb_dist,carn_dist,cmap)
        self.update_fitness_histogram([],[],hist_specs['fitness'])
        self.update_weight_histogram([],[],hist_specs['weight'])
        self.update_age_histogram([],[],hist_specs['age'])
        self.year_counter = self.fig.add_axes([0.4, 0.8, 0.2, 0.2])  # llx, lly, w, h
        self.year_counter.axis('off')  # turn off coordinate system
        self.year_txt = self.year_counter.text(0.5, 0.5, self.year_template.format(0),
                                               horizontalalignment='center',
                                               verticalalignment='center',
                                               transform=self.year_counter.transAxes)
        self.img_years = img_years
        # if self.img_dir is not None and os.path.exists(self.img_dir):
        #     for filename in os.listdir(self.img_dir):
        #         file_path = os.path.join(self.img_dir, filename)
        #         try:
        #             if os.path.isfile(file_path) or os.path.islink(file_path):
        #                 os.unlink(file_path)
        #             elif os.path.isdir(file_path):
        #                 shutil.rmtree(file_path)
        #         except Exception as e:
        #             print('Failed to delete %s. Reason: %s' % (file_path, e))

        if not os.path.exists(self.img_dir):
            os.mkdir(self.img_dir)

        self.show_plots()

    def make_map(self, map_rgb):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Geography'][0]
        ax.imshow(map_rgb)
        ax.set_xticks(range(len(map_rgb[0])))
        ax.set_xticklabels(range(1, 1 + len(map_rgb[0])))
        ax.set_yticks(range(len(map_rgb)))
        ax.set_yticklabels(range(1, 1 + len(map_rgb)))

    def update_visualization(self, year, total_years,cmax_animals, hist_specs, y_max,
                             herbivore_data, carnivore_data):
        self.update_number_of_species_graph(False, year, total_years, herbivore_data["count"],
                                            carnivore_data["count"], y_max)
        self.update_distribution_map(herbivore_data["distribution"], carnivore_data["distribution"],cmax_animals)
        self.update_fitness_histogram(herbivore_data["fitness"],carnivore_data["fitness"],hist_specs['fitness'])
        self.update_weight_histogram(herbivore_data["weight"],carnivore_data["weight"],hist_specs['weight'])
        self.update_age_histogram(herbivore_data["age"],carnivore_data["age"],hist_specs['age'])
        self.year_txt.set_text(self.year_template.format(year))
        self.show_plots()
        self._save_graphics(year)

    def update_number_of_species_graph(self, is_init, current_year, total_years, herbivore_count, carnivores_count,
                                       y_max):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Number_of_species'][0]
        max_count = max(herbivore_count, carnivores_count)
        if y_max is not None:
            self.max_species_count = y_max
        if is_init:
            ax.set_xlim(0, total_years)
            ax.set_ylim(0, self.max_species_count)
            self.line_herbivores = ax.plot(np.arange(total_years),
                                           np.full(total_years, np.nan), 'b-')[0]
            self.line_carnivores = ax.plot(np.arange(total_years),
                                           np.full(total_years, np.nan), 'r-')[0]
        else:
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
            if self.max_species_count < max_count:
                self.max_species_count = int(1.2 * max_count)
                ax.set_ylim(0, self.max_species_count)
        y_data_herbivore = self.line_herbivores.get_ydata()
        y_data_herbivore[current_year - 1] = herbivore_count
        y_data_carnivore = self.line_carnivores.get_ydata()
        y_data_carnivore[current_year - 1] = carnivores_count
        self.line_herbivores.set_ydata(y_data_herbivore)
        self.line_carnivores.set_ydata(y_data_carnivore)

    def update_distribution_map(self,herbivore_map, carnivore_map,cmax_animals):
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

    def update_fitness_histogram(self,fitness_values_herbivores, fitness_values_carnivores ,fitness_hist_specs):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Fitness_Histogram'][0]
        ax.clear()
        ax.set_title('Fitness histogram',
                     verticalalignment='bottom')
        bins = int(fitness_hist_specs['max'] / fitness_hist_specs['delta'])
        ax.hist((fitness_values_herbivores, fitness_values_carnivores), bins,
                (0, fitness_hist_specs['max']), histtype='step', linewidth=3,
                label=('Herbivores', 'Carnivores'), color=('b', 'r'))
        ax.legend()

    def update_age_histogram(self,age_values_herbivores, age_values_carnivores , age_hist_specs):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Age_Histogram'][0]
        ax.clear()
        ax.set_title('Age histogram',
                     verticalalignment='bottom')
        bins_age = int(age_hist_specs['max'] / age_hist_specs['delta'])
        ax.hist((age_values_herbivores, age_values_carnivores), bins_age,
                (0, age_hist_specs['max']), histtype='step', linewidth=3,
                label=('Herbivores', 'Carnivores'), color=('b', 'r'))
        ax.legend()

    def update_weight_histogram(self,weight_values_herbivores, weight_values_carnivores, weight_hist_specs):
        ax = [pt['Plot'] for pt in self.plots if pt['Name'] == 'Weight_Histogram'][0]
        ax.clear()
        ax.set_title('Weight histogram',
                     verticalalignment='bottom')
        bins = int(weight_hist_specs['max'] / weight_hist_specs['delta'])
        ax.hist((weight_values_herbivores, weight_values_carnivores), bins,
                (0, weight_hist_specs['max']), histtype='step', linewidth=3,
                label=('Herbivores', 'Carnivores'), color=('b', 'r'))
        ax.legend()

    def _save_graphics(self, year):
        """Saves graphics to file if file name given."""

        if self._img_base is None or year % self.img_years != 0:
            return

        plt.savefig('{base}_{num:05d}.{type}'.format(base=self._img_base,
                                                     num=self._img_ctr,
                                                     type=self._img_fmt))
        self._img_ctr += 1

    def make_movie(self, movie_fmt=None):
        """
        Creates MPEG4 movie from visualization images saved.

        .. :note:
            Requires ffmpeg for MP4 and magick for GIF

        The movie is stored as img_base + movie_fmt
        """

        if self._img_base is None:
            raise RuntimeError("No filename defined.")

        if movie_fmt is None:
            movie_fmt = _DEFAULT_MOVIE_FORMAT

        if movie_fmt == 'mp4':
            try:
                # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
                # section "Compatibility"
                subprocess.check_call([_FFMPEG_BINARY,
                                       '-i', '{}_%05d.png'.format(self._img_base),
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '3.0',
                                       '-pix_fmt', 'yuv420p',
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: ffmpeg failed with: {}'.format(err))
        elif movie_fmt == 'gif':
            try:
                subprocess.check_call([_MAGICK_BINARY,
                                       '-delay', '1',
                                       '-loop', '0',
                                       '{}_*.png'.format(self._img_base),
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: convert failed with: {}'.format(err))
        else:
            raise ValueError('Unknown movie format: ' + movie_fmt)
