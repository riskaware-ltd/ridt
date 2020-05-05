from config import IDMFConfig
from config.idmfconfig import Plane

from matplotlib import cm, ticker
import matplotlib.pyplot as plt
import numpy as np


class ContourPlot:

    def __init__(self, settings: IDMFConfig):
        self.settings = settings

        self.sources = getattr(
            self.settings.modes, self.settings.release_type).sources

    def __call__(self, concentrations: np.ndarray, plane: Plane, time: float, save_dir):
        self.plot(concentrations, plane)
        self.save_fig(plane, time, save_dir)

    def plot(self, concentrations: np.ndarray, plane: Plane):
        title = self.make_title(plane)

        x_range = np.array([i for i in range(len(concentrations))])
        y_range = np.array([i for i in range(len(concentrations[0]))])

        plot = plt.contourf(
            x_range, y_range, concentrations,
            levels=self.__calculate_levels(), extend="min",
            locator=ticker.LinearLocator(),
            cmap=cm.RdBu)

        plt.colorbar()
        plt.title(title)
        self.__set_labels(plane)

        return plot

    def save_fig(self, plane: Plane, time, save_dir):
        plt.savefig(f"{save_dir}/{self.settings.dispersion_model.capitalize()} "
                    f"{self.settings.release_type.capitalize()} {len(self.sources)} Source(s) "
                    f"{plane.axis} plane, "
                    f"{plane.distance} distance, "
                    f"time {time}.pdf")

    def make_title(self, plane: Plane):
        title = f"{self.settings.dispersion_model.capitalize()} model with " \
                f"{self.settings.release_type.capitalize()} release type."
        for key, val in self.sources.items():
            if self.settings.release_type == "instantaneous":
                title += f" \n{key} at {[val.x, val.y, val.z]}, mass of {val.mass}, release time {val.time}."
            elif self.settings.release_type == "infinite_duration":
                title += f" \n{key} at {[val.x, val.y, val.z]}, rate of {val.rate}, release time {val.time}."
            elif self.settings.release_type == "fixed_duration":
                title += f" \n{key} at {[val.x, val.y, val.z]}, rate of {val.rate}, start time {val.start_time}," \
                         f" end time {val.end_time}."
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


from config.configfileparser import ConfigFileParser
from config.configfileparser import ConfigFileParserJSONError
from config.configfileparser import ConfigFileParserOSError
from config.configfileparser import ConfigFileParserValidationError
import sys

try:
    with ConfigFileParser() as cfp:
        s = cfp("../default/config.json")
except (ConfigFileParserJSONError,
        ConfigFileParserOSError,
        ConfigFileParserValidationError) as e:
    sys.exit(e)

plane_dict = {
        "axis": "yz",
        "distance": 0.1
    }

plane = Plane(plane_dict)

conc_x = [i for i in range(-10, 10)]
conc_y = [i for i in range(-10, 10)]

xx, yy = np.meshgrid(conc_x, conc_y)
time = 10


def function(x, y):
    return np.sin(x) - np.cos(y) + np.random.normal()


zz = function(xx, yy)

cp = ContourPlot(s)
cp(zz, plane, time, "C:/Work/EDM/idmf/analysis")