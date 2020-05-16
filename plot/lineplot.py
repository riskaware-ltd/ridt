from config import IDMFConfig
from config import Line

from typing import List

import matplotlib.pyplot as plt
import numpy as np


class LinePlot:

    def __init__(self, settings: IDMFConfig, output_dir: str):
        self.settings = settings
        self.output_dir = output_dir

        self.time_array = np.linspace(
            0, settings.total_time, settings.time_samples)

    def __call__(self, concentrations: List[float], line: Line):
        for idx, time in enumerate(self.time_array):
            self.plot(concentrations, line)
            self.save_fig(line, idx)
            plt.clf()

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
                    f"Line {line.point.x, line.point.y, line.point.z}, "
                    f"along {line.parallel_axis} axis "
                    f"time index {time}.pdf")

    def make_title(self, line: Line):
        title = f"{self.settings.dispersion_model.capitalize()}" \

        title += f" \n From {[line.point.x, line.point.y, line.point.z]}, " \
                 f"in {line.parallel_axis} axis"
        return title
