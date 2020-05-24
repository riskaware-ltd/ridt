import os

from config import IDMFConfig

from container.domain import Domain

from typing import List

import matplotlib.pyplot as plt


class PointPlot:

    def __init__(self, settings: IDMFConfig, output_dir: str):
        self.settings = settings
        self.output_dir = output_dir

        self.domain = Domain(self.settings)

    def __call__(self,
                 concentrations: List[float],
                 plot_type: str,
                 point_name: str = None):
        self.point_name = point_name
        self.dir_name = "PointPlots"
        try:
            os.mkdir(f"{self.output_dir}/{self.dir_name}")
        except FileExistsError:
            pass

        self.plot_type = plot_type
        self.plot(concentrations)
        self.save_fig()
        plt.clf()

    def plot(self, concentrations: List[float]):
        title = self.make_title()

        plt.title(title)
        plt.ylabel(
            f"{self.plot_type.capitalize()} "
            f"({getattr(self.settings, f'{self.plot_type}_units')})")
        plt.xlabel(f"Time ({self.settings.time_units})")

        plot = plt.plot(self.domain.time, concentrations)

        return plot

    def save_fig(self):
        name = f"{self.output_dir}/{self.dir_name}/{self.settings.dispersion_model.capitalize()}"
        if self.point_name:
            name += f" {self.point_name.capitalize()}"
        plt.savefig(f"{name}.pdf")

    def make_title(self):
        title = f"{self.plot_type.capitalize()} vs time at " \
                f"{self.point_name.capitalize()}"
        return title
