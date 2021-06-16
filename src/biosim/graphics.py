import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess
from matplotlib import gridspec, rcParams

# If you installed ffmpeg using conda or installed both softwares in
# standard ways on your computer, no changes should be required.

_FFMPEG_BINARY = 'ffmpeg'
_MAGICK_BINARY = 'magick'
rcParams["legend.loc"] = 'upper left'
rcParams["legend.fontsize"] = 6

# update this to the directory and file-name beginning
# for the graphics files
_DEFAULT_GRAPHICS_DIR = os.path.join('..', 'data')
_DEFAULT_GRAPHICS_NAME = 'dv'
_DEFAULT_IMG_FORMAT = 'png'
_DEFAULT_MOVIE_FORMAT = 'mp4'  # alternatives: mp4, gif


class Graphics:
    def __init__(self, img_dir=None, img_name=None, img_fmt=None):
        self.fig = None
        self.geography_ax = None
        self.species_count_ax = None
        self.herbivore_dist_ax = None
        self.carnivore_dist_ax = None
        self.fitness_hist_ax = None
        self.age_hist_ax = None
        self.weight_hist_ax = None
        self.line_herbivores = []
        self.line_carnivores = []
        self.herb_dist_axis = None
        self.carn_dist_axis = None
        self.max_species_count = 1000
        self.year_counter = None
        self.plt_fig_title = None
        self.plt_fig_title_txt = None
        self.slctd_cl_ax = None
        self.selected_cell_ax_txt = None
        self.plt_fig_title_txt = None
        self.year_txt = None
        self._map_legend_ax = None
        self.year_template = 'Year: {:5d}'
        self._gs = None
        self.cell_list = []
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
        """
                Shows and refreshes plots

        |

        """
        self.fig.canvas.flush_events()
        plt.pause(1e-6)

    def setup_visualization(self, total_years, cmap, hist_specs, y_max,
                            img_years, map_rgb, herb_dist, carn_dist):
        """
                Setup graphics

        |

        """
        self.fig = plt.figure(constrained_layout=True)
        self._gs = gridspec.GridSpec(ncols=4, nrows=3, figure=self.fig)
        self.geography_ax = self.fig.add_subplot(self._gs[0:2, 1:3])
        self.species_count_ax = self.fig.add_subplot(self._gs[0, 0])
        self.herbivore_dist_ax = self.fig.add_subplot(self._gs[1, 0])
        self.carnivore_dist_ax = self.fig.add_subplot(self._gs[2, 0])
        self.fitness_hist_ax = self.fig.add_subplot(self._gs[0, 3])
        self.age_hist_ax = self.fig.add_subplot(self._gs[1, 3])
        self.weight_hist_ax = self.fig.add_subplot(self._gs[2, 3])
        self._map_legend_ax = self.fig.add_axes([0.36, 0.22, 0.43, 0.2])
        self._map_legend_ax.axis('off')
        self.slctd_cl_ax = self.fig.add_axes([0.33, 0.28, 0.43, 0.1])
        self.slctd_cl_ax.axis('off')
        self.year_counter = self.fig.add_axes([0.4, 0.05, 0.3, 0.2])  # llx, lly, w, h
        self.year_counter.axis('off')  # turn off coordinate system
        self.plt_fig_title = self.fig.add_axes([0.3, 0., 0.5, 0.2])  # llx, lly, w, h
        self.plt_fig_title.axis('off')  # turn off coordinate system
        self.make_map(map_rgb)
        self.update_number_of_species_graph(True, 0, total_years, 0, 0, y_max)
        self.update_distribution_map(herb_dist, carn_dist, cmap)
        self.update_fitness_histogram([], [], hist_specs['fitness'])
        self.update_weight_histogram([], [], hist_specs['weight'])
        self.update_age_histogram([], [], hist_specs['age'])
        self.year_txt = self.year_counter.text(0.5, 0.5, self.year_template.format(0),
                                               horizontalalignment='center',
                                               verticalalignment='center',
                                               transform=self.year_counter.transAxes, fontsize=14)
        self.plt_fig_title_txt = self.plt_fig_title.text(0.5, 0.5, self.year_template.format(0),
                                                         horizontalalignment='center',
                                                         verticalalignment='center',
                                                         transform=self.plt_fig_title.transAxes,
                                                         fontsize=14,
                                                         fontweight='bold')
        self.plt_fig_title_txt.set_text("BioSim: Population Dynamics Simulation")

        self.selected_cell_ax_txt = self.slctd_cl_ax.text(0.5, 0.5,
                                                          self.year_template.format(0),
                                                          horizontalalignment='center',
                                                          verticalalignment='center',
                                                          transform=self.slctd_cl_ax.transAxes,
                                                          fontsize=8
                                                          )
        self.selected_cell_ax_txt.set_text("")
        # self.fig.canvas.manager.full_screen_toggle()

        self.img_years = img_years
        if not os.path.exists(self.img_dir):
            os.mkdir(self.img_dir)

        self.show_plots()
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)

    def make_map(self, map_rgb):
        """
                Makes map for the island

        |

        """
        self.geography_ax.imshow(map_rgb)
        update_plot_tick_labels(self.geography_ax, map_rgb)
        self.geography_ax.set_title("Island", fontweight='bold')
        rgb_value = {'W': (0.0, 0.0, 1.0),  # blue
                     'L': (0.0, 0.6, 0.0),  # dark green
                     'H': (0.5, 1.0, 0.5),  # light green
                     'D': (1.0, 1.0, 0.5)}  # light yellow
        for i, name in enumerate(('Water', 'Lowland',
                                  'Highland', 'Desert')):
            self._map_legend_ax.add_patch(plt.Rectangle(xy=(i * 0.25, 0.), width=0.14, height=0.15,
                                                        edgecolor='none',
                                                        facecolor=rgb_value[name[0]]))
            self._map_legend_ax.text(i * 0.25, 0.2, name, transform=self._map_legend_ax.transAxes)

    def update_visualization(self, year, total_years, cmax_animals, hist_specs, y_max,
                             herbivore_data, carnivore_data, cell_list):
        """
            Updates graphics based on current state of the simulation

        |

        """
        self.cell_list = cell_list
        self.update_number_of_species_graph(False, year, total_years, herbivore_data["count"],
                                            carnivore_data["count"], y_max)
        self.update_distribution_map(herbivore_data["distribution"],
                                     carnivore_data["distribution"], cmax_animals)
        self.update_fitness_histogram(herbivore_data["fitness"],
                                      carnivore_data["fitness"], hist_specs['fitness'])
        self.update_weight_histogram(herbivore_data["weight"],
                                     carnivore_data["weight"], hist_specs['weight'])
        self.update_age_histogram(herbivore_data["age"],
                                  carnivore_data["age"], hist_specs['age'])
        self.year_txt.set_text(self.year_template.format(year))
        self.show_plots()
        if self.img_years > 0:
            self._save_graphics(year)

    def update_number_of_species_graph(self, is_init, current_year, total_years,
                                       herbivore_count, carnivores_count, y_max):
        """
            Updates number of species count graph

        |

        """
        max_count = max(herbivore_count, carnivores_count)
        if y_max is not None:
            self.max_species_count = y_max
        if is_init:
            self.species_count_ax.set_xlim(0, total_years)
            self.species_count_ax.set_ylim(0, self.max_species_count)
            self.line_herbivores = self.species_count_ax.plot(np.arange(total_years),
                                                              np.full(total_years, np.nan),
                                                              'b-', lw=1, label='H')[0]
            self.line_carnivores = self.species_count_ax.plot(np.arange(total_years),
                                                              np.full(total_years, np.nan),
                                                              'r-', lw=1, label='C')[0]
            self.species_count_ax.set_title("Animal Count", fontstyle='italic')
            self.species_count_ax.patch.set_facecolor('gainsboro')
            self.species_count_ax.legend()
        else:
            if total_years > len(self.line_herbivores.get_xdata()):
                x_data_h, y_data_h = self.line_herbivores.get_data()
                x_data_c, y_data_c = self.line_carnivores.get_data()
                x_new_h = np.arange(x_data_h[-1] + 1, total_years + 1)
                x_new_c = np.arange(x_data_c[-1] + 1, total_years + 1)
                self.species_count_ax.set_xlim(0, total_years + 1)
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
                self.species_count_ax.set_ylim(0, self.max_species_count)
        y_data_herbivore = self.line_herbivores.get_ydata()
        y_data_herbivore[current_year - 1] = herbivore_count
        y_data_carnivore = self.line_carnivores.get_ydata()
        y_data_carnivore[current_year - 1] = carnivores_count
        self.line_herbivores.set_ydata(y_data_herbivore)
        self.line_carnivores.set_ydata(y_data_carnivore)

    def update_distribution_map(self, herbivore_map, carnivore_map, cmax_animals):
        """
            Updates distribution maps

        |

        """
        if self.herb_dist_axis is not None:
            self.herb_dist_axis.set_data(herbivore_map)
            self.herbivore_dist_ax.set_title("Herbivore Distribution", fontstyle='italic')
            update_plot_tick_labels(self.herbivore_dist_ax, herbivore_map)
        else:
            self.herb_dist_axis = self.herbivore_dist_ax.imshow(herbivore_map,
                                                                interpolation='nearest',
                                                                vmin=-0.25,
                                                                vmax=cmax_animals['Herbivore'],
                                                                cmap='Greens'
                                                                )
            plt.colorbar(self.herb_dist_axis, ax=self.herbivore_dist_ax,
                         orientation='vertical')

        if self.carn_dist_axis is not None:
            self.carn_dist_axis.set_data(carnivore_map)
            self.carnivore_dist_ax.set_title("Carnivore Distribution", fontstyle='italic')
            update_plot_tick_labels(self.carnivore_dist_ax, carnivore_map)
        else:
            self.carn_dist_axis = self.carnivore_dist_ax.imshow(carnivore_map,
                                                                interpolation='nearest',
                                                                vmin=-0.25,
                                                                vmax=cmax_animals['Carnivore'],
                                                                cmap='Reds'
                                                                )
            plt.colorbar(self.carn_dist_axis, ax=self.carnivore_dist_ax,
                         orientation='vertical')

    def update_fitness_histogram(self, fitness_values_herbivores,
                                 fitness_values_carnivores, fitness_hist_specs):
        """
            Updates fitness histograms

        |

        """
        self.fitness_hist_ax.clear()
        self.fitness_hist_ax.set_title("Fitness", fontstyle='italic')
        bins = get_bins(fitness_hist_specs)
        self.fitness_hist_ax.hist((fitness_values_herbivores, fitness_values_carnivores), bins,
                                  (0, fitness_hist_specs['max']), histtype='step', linewidth=1,
                                  label=('Herbivores', 'Carnivores'), color=('b', 'r'))
        self.fitness_hist_ax.patch.set_facecolor('gainsboro')

    def update_age_histogram(self, age_values_herbivores, age_values_carnivores, age_hist_specs):
        """
            Updates age histograms

        |

        """
        self.age_hist_ax.clear()
        self.age_hist_ax.set_title("Age", fontstyle='italic')
        bins = get_bins(age_hist_specs)
        self.age_hist_ax.hist((age_values_herbivores, age_values_carnivores), bins,
                              (0, age_hist_specs['max']), histtype='step', linewidth=1,
                              label=('Herbivores', 'Carnivores'), color=('b', 'r'))
        self.age_hist_ax.patch.set_facecolor('gainsboro')

    def update_weight_histogram(self, weight_values_herbivores,
                                weight_values_carnivores, weight_hist_specs):
        """
            Updates weight histograms

        |

        """
        self.weight_hist_ax.clear()
        self.weight_hist_ax.set_title("Weight", fontstyle='italic')
        bins = get_bins(weight_hist_specs)
        self.weight_hist_ax.hist((weight_values_herbivores, weight_values_carnivores), bins,
                                 (0, weight_hist_specs['max']), histtype='step', linewidth=1,
                                 label=('H', 'C'), color=('b', 'r'))
        self.weight_hist_ax.patch.set_facecolor('gainsboro')

    def _save_graphics(self, year):
        """
            Saves graphics to file if file name given.

        |

        """
        if self._img_base is None or year % self.img_years != 0:
            return

        plt.savefig('{base}_{num:05d}.{type}'.format(base=self._img_base,
                                                     num=self._img_ctr,
                                                     type=self._img_fmt))
        self._img_ctr += 1

    def on_press(self, event):
        if event.inaxes == self.geography_ax:
            loc = (int(event.ydata) + 1, int(event.xdata) + 1)
            cell = next((cl for cl in self.cell_list if cl.loc[0] == int(event.ydata) + 1
                         and cl.loc[1] == int(event.xdata) + 1), None)
            if cell is not None:
                txt = "Location:" + str(loc) + "    Cell Type:"\
                      + str(cell.__class__.__name__) +\
                      "    Herbivores:" + str(
                    len(cell.herbivores)) + "    Carnivores:" + str(len(cell.carnivores))
                self.selected_cell_ax_txt.set_text(txt)

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


def get_bins(spec):
    """
        Calculate bins count

    |

    """
    return int(spec['max'] / spec['delta'])


def update_plot_tick_labels(plot, data):
    """
        Set ticks labels for graphs

    |

    """
    plot.set_xticks(np.arange(0, len(data[0]), 5))
    plot.set_xticklabels(np.arange(1, len(data[0]) + 1, 5))
    plot.set_yticks(np.arange(0, len(data), 2))
    plot.set_yticklabels(np.arange(1, len(data) + 1, 2))
