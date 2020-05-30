import math

from os.path import join

from numpy import ndarray
from numpy import max

from config import RIDTConfig
from config import Units

from container import Domain

from typing import List

import matplotlib.pyplot as plt


class PointPlot:

    def __init__(self, settings: RIDTConfig, output_dir: str, quantity: str):
        self.settings = settings
        self.output_dir = output_dir
        self.units = Units(settings)
        self.domain = Domain(self.settings)
        self.quantity = quantity
        self.config = self.settings.models.eddy_diffusion.points_plots

    def __call__(self, id: str, data: ndarray):
        self.id = id 
        self.plot(data)
        plt.tight_layout()
        self.save_fig()
        plt.clf()

    def plot(self, data: ndarray):
        plt.title(self.title())
        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())
        if min(data) > 0.0:
            pass
        else:
            plt.ylim(1e-34, 1**(int(math.log10(max(data))) + 1))
        if self.config.scale == "logarithmic":
            plt.yscale("log")
        plot = plt.plot(self.domain.time, data, marker='.')
        return plot

    def save_fig(self):
        plt.savefig(join(self.output_dir, f"{self.id}.png"))

    def title(self):
        return f"{self.quantity} vs time - {self.id}"

    def ylabel(self):
        return f"{self.quantity} ({getattr(self.units, f'{self.quantity}')})"

    def xlabel(self):
        return f"Time ({self.settings.time_units})"
