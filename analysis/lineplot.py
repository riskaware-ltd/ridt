from config import IDMFConfig
from config.idmfconfig import Line

from typing import List

import matplotlib.pyplot as plt
import numpy as np


class LinePlot:

    def __init__(self, settings: IDMFConfig):
        self.settings = settings

        self.sources = getattr(
            self.settings.modes, self.settings.release_type).sources

    def __call__(self, concentrations: List[float], line: Line, time: float, save_dir):
        self.plot(concentrations, line)
        self.save_fig(line, time, save_dir)

    def plot(self, concentrations: List[float], line: Line):
        title = self.make_title(line)

        x_range = np.array([i for i in range(len(concentrations))])
        x_range = x_range / max(x_range)

        plt.title(title)
        plt.ylabel(f"Concentration in {self.settings.concentration_units}")
        plt.xlabel(f"Relative unit along line")

        plot = plt.plot(x_range, concentrations)

        return plot

    def save_fig(self, line: Line, time, save_dir):
        plt.savefig(f"{save_dir}/{self.settings.dispersion_model.capitalize()} "
                    f"{self.settings.release_type.capitalize()} {len(self.sources)} Source(s) "
                    f"Line {line.pointA.x, line.pointA.y, line.pointA.z}, "
                    f"to {line.pointB.x, line.pointB.y, line.pointB.z} "
                    f"time {time}.pdf")

    def make_title(self, line: Line):
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

        title += f" \n From {[line.pointA.x, line.pointA.y, line.pointA.z]}, " \
                 f"to {[line.pointB.x, line.pointB.y, line.pointB.z]}"
        return title
