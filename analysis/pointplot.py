from config import IDMFConfig
from config.idmfconfig import Point

from typing import List

import matplotlib.pyplot as plt
import numpy as np


class PointPlot:

    def __init__(self, settings: IDMFConfig):
        self.settings = settings

        self.sources = getattr(
            self.settings.modes, self.settings.release_type).sources
        self.t_array = np.linspace(
            0, settings.total_time, settings.time_samples)

    def __call__(self,
                 concentrations: List[float],
                 point: Point = None):

        self.plot(concentrations)
        self.save_fig(point)

    def plot(self, concentrations: List[float]):
        title = self.make_title()

        plt.title(title)
        plt.ylabel(f"Concentration ({self.settings.concentration_units})")
        plt.xlabel(f"time ({self.settings.time_units})")

        plot = plt.plot(self.t_array, concentrations)

        return plot

    def save_fig(self, point: Point = None):
        name = f"{self.settings.output_dir}/{self.settings.dispersion_model.capitalize()} " \
               f"{self.settings.release_type.capitalize()} {len(self.sources)} Source(s)"
        if point:
            name += f" Point at {[point.x, point.y, point.z]}"

        plt.savefig(f"{name}.pdf")

    def make_title(self):
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
        return title
