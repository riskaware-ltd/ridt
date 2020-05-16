from config import IDMFConfig
from config import Plane

from matplotlib import cm, ticker
import matplotlib.pyplot as plt

import numpy as np


class ContourPlot:

    def __init__(self, settings: IDMFConfig, output_dir: str):
        self.settings = settings
        self.output_dir = output_dir

        self.time_array = np.linspace(
            0, settings.total_time, settings.time_samples)

    def __call__(self, concentrations: np.ndarray, plane: Plane):
        for idx, time in enumerate(self.time_array):
            self.plot(concentrations[idx], plane)
            self.save_fig(plane, idx)
            plt.clf()

    def plot(self, concentrations: np.ndarray, plane: Plane):
        title = self.make_title(plane)

        x_range = np.array([i for i in range(len(concentrations))])
        y_range = np.array([i for i in range(len(concentrations[0]))])

        plot = plt.contourf(
            x_range, y_range, concentrations,
            levels=self.__calculate_levels(), extend="min",
            locator=ticker.LinearLocator(),
            cmap=cm.RdBu)

        plt.title(title)
        self.__set_labels(plane)

        return plot

    def save_fig(self, plane: Plane, time):
        plt.savefig(f"{self.output_dir}/{self.settings.dispersion_model.capitalize()} "
                    f"{plane.axis} plane, "
                    f"{plane.distance} distance, "
                    f"time index {time}.pdf")

    def make_title(self, plane: Plane):
        title = f"{self.settings.dispersion_model.capitalize()} model with "
        title += f" \n Plane parallel to {plane.axis} axis, " \
                 f"located {plane.distance} {self.settings.models.eddy_diffusion.spatial_units} along "
        return title

    def __calculate_levels(self):
        contour_plots = self.settings.models.eddy_diffusion.contour_plots
        if contour_plots.range == "auto":
            return
        else:
            contour_range = np.linspace(
                contour_plots.contours.min,
                contour_plots.contours.max,
                contour_plots.number_of_contours
            )
            return contour_range

    def __set_labels(self, plane: Plane):
        for idx, axis in enumerate(list(plane.axis)):
            if idx == 0:
                plt.xlabel(f"Distance along {axis} axis ({self.settings.models.eddy_diffusion.spatial_units})")
            if idx == 1:
                plt.ylabel(f"Distance along {axis} axis ({self.settings.models.eddy_diffusion.spatial_units})")
