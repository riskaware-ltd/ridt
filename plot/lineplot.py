import os

from config import IDMFConfig
from config import Line

from container.domain import Domain

from typing import List

import matplotlib.pyplot as plt
import numpy as np


class LinePlot:

    def __init__(self, settings: IDMFConfig, output_dir: str):
        self.settings = settings
        self.output_dir = output_dir

        self.domain = Domain(self.settings)

    def __call__(self,
                 concentrations: np.ndarray,
                 line: Line,
                 line_name: str,
                 plot_type: str,
                 min_value: float,
                 max_value: float):

        """Future Reference: plot_type must be either concentration or exposure."""

        self.line_name = line_name
        self.dir_name = "LinePlots"
        try:
            os.mkdir(f"{self.output_dir}/{self.dir_name}")
        except FileExistsError:
            pass

        self.min = min_value
        self.max = max_value
        self.plot_type = plot_type
        for idx, time in enumerate(self.domain.time):
            self.plot(concentrations[idx], line)
            self.save_fig(round(time, 1))
            plt.close()

    def plot(self, concentrations: np.ndarray, line: Line):
        title = self.make_title()

        x_range = self.__get_ranges(line)

        plt.ylim(self.min, self.max)

        plt.title(title)
        plt.ylabel(
            f"{self.plot_type.capitalize()} "
            f"({getattr(self.settings, f'{self.plot_type}_units')})")
        plt.xlabel(f"Distance ({line.parallel_axis})")

        plot = plt.plot(x_range, concentrations)

        return plot

    def save_fig(self, time):
        plt.savefig(f"{self.output_dir}/{self.dir_name}/{self.settings.dispersion_model.capitalize()} "
                    f"{self.line_name.capitalize()}, "
                    f"time = {time}.pdf")

    def make_title(self):
        title = f"{self.plot_type.capitalize()} vs time at " \
                f"{self.line_name.capitalize()}"
        return title

    def __get_ranges(self, line: Line):
        x_range = getattr(self.domain, line.parallel_axis)
        return x_range
