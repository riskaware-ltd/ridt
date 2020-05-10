from config import IDMFConfig
from config.idmfconfig import Line

from typing import List

import matplotlib.pyplot as plt
import numpy as np


class LinePlot:

    def __init__(self, settings: IDMFConfig, output_dir: str):
        self.settings = settings
        self.output_dir = output_dir

    def __call__(self, concentrations: List[float], line: Line, time: float):
        self.plot(concentrations, line)
        self.save_fig(line, time)

    def plot(self, concentrations: List[float], line: Line):
        title = self.make_title(line)

        x_range = np.array([i for i in range(len(concentrations))])
        x_range = x_range / max(x_range)

        plt.title(title)
        plt.ylabel(f"Concentration in {self.settings.concentration_units}")
        plt.xlabel(f"Relative unit along line")

        plot = plt.plot(x_range, concentrations)

        return plot

    def save_fig(self, line: Line, time):
        plt.savefig(f"{self.output_dir}/{self.settings.dispersion_model.capitalize()} "
                    f"Line {line.pointA.x, line.pointA.y, line.pointA.z}, "
                    f"to {line.pointB.x, line.pointB.y, line.pointB.z} "
                    f"time {time}.pdf")

    def make_title(self, line: Line):
        title = f"{self.settings.dispersion_model.capitalize()}" \

        title += f" \n From {[line.start_point.x, line.start_point.y, line.start_point.z]}, " \
                 f"length {line.length} in {line.direction} axis"
        return title
