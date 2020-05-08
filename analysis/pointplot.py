from config import IDMFConfig
from config.idmfconfig import Point

from typing import List

import matplotlib.pyplot as plt
import numpy as np


class PointPlot:

    def __init__(self, settings: IDMFConfig, output_dir: str):
        self.settings = settings
        self.output_dir = output_dir

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
        name = f"{self.output_dir}/{self.settings.dispersion_model.capitalize()} "
        if point:
            name += f" Point at {[point.x, point.y, point.z]}"

        plt.savefig(f"{name}.pdf")

    def make_title(self):
        title = f"{self.settings.dispersion_model.capitalize()} model with "
        
        return title
