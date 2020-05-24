import os
import sys

from config import IDMFConfig
from config import Plane

from matplotlib import cm, ticker
import matplotlib.pyplot as plt

import numpy as np

from container.domain import Domain


class ContourPlot:

    def __init__(self, settings: IDMFConfig, output_dir: str):
        self.settings = settings
        self.output_dir = output_dir

        self.domain = Domain(self.settings)

    def __call__(self,
                 concentrations: np.ndarray,
                 plane: Plane,
                 plane_name: str,
                 plot_type: str,
                 min_value: float,
                 max_value: float):

        self.plane = plane
        self.plane_name = plane_name
        self.dir_name = "ContourPlots"
        try:
            os.mkdir(f"{self.output_dir}/{self.dir_name}")
        except FileExistsError:
            pass

        self.min = min_value + 0.1
        self.max = max_value
        self.plot_type = plot_type
        for idx, time in enumerate(self.domain.time):
            self.plot(concentrations[idx], plane)
            self.save_fig(round(time, 1))
            plt.close()

    def plot(self, concentrations: np.ndarray, plane: Plane):
        try:
            title = self.make_title()

            x_range, y_range = self.__get_ranges()

            plot = plt.contourf(
                x_range, y_range, concentrations,
                levels=self.__calculate_levels(), extend="min",
                cmap=cm.RdBu)

            plt.clim(self.min, self.max)
            plt.colorbar()

            plt.title(title)
            self.__set_labels(plane)

            return plot
        except ValueError:
            print("Must have at least two contours. Try using "
                  "linear scaling.")
            sys.exit()

    def save_fig(self, time):
        plt.savefig(f"{self.output_dir}/{self.dir_name}/{self.settings.dispersion_model.capitalize()} "
                    f"{self.plane_name.capitalize()}, "
                    f"time = {time}.pdf")

    def make_title(self):
        title = f"{self.plot_type.capitalize()} at " \
                f"{self.plane_name.capitalize()}"
        return title

    def __calculate_levels(self):
        contour_plots = self.settings.models.eddy_diffusion.contour_plots
        if contour_plots.range == "auto":
            contour_range = np.linspace(
                self.min,
                self.max,
                contour_plots.number_of_contours
            )
        else:
            contour_range = np.linspace(
                contour_plots.contours.min,
                contour_plots.contours.max,
                contour_plots.number_of_contours
            )
        if contour_plots.scale == "logarithmic":
            lev_exp = np.arange(np.floor(np.log10(self.min) - 1),
                                np.ceil(np.log10(self.max) + 1))
            contour_range = np.power(10, lev_exp)
        return contour_range

    def __get_ranges(self):
        x_range = getattr(self.domain, list(self.plane.axis)[0])
        y_range = getattr(self.domain, list(self.plane.axis)[1])
        return x_range, y_range

    def __set_labels(self, plane: Plane):
        for idx, axis in enumerate(list(plane.axis)):
            if idx == 0:
                plt.xlabel(f"{axis} ({self.settings.models.eddy_diffusion.spatial_units})")
            if idx == 1:
                plt.ylabel(f"{axis} ({self.settings.models.eddy_diffusion.spatial_units})")
