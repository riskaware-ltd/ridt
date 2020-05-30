import math

from os.path import join

from numpy import ndarray
from numpy import power

from config import IDMFConfig
from config import Units

from container import Domain

from typing import List

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib import animation

class LinePlot:

    def __init__(self, settings: IDMFConfig, output_dir: str, quantity: str):
        self.settings = settings
        self.output_dir = output_dir
        self.units = Units(settings)
        self.domain = Domain(self.settings)
        self.quantity = quantity
        self.config = self.settings.models.eddy_diffusion.lines_plots

    def __call__(self, id: str, data: ndarray, max_val: float, t_index: int):
        self.id = id
        self.t_index = t_index
        self.max_val = max_val
        self.axis = self.get_axis()
        self.plot(data)
        plt.tight_layout()
        self.save_fig()
        plt.close()

    def plot(self, data: ndarray):

        plt.title(self.title())
        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())

        plt.ylim(1e-34, 1**(int(math.log10(self.max_val)) + 1))
        plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%.d'))
        if self.config.scale == "logarithmic":
            plt.yscale("log")

        plot = plt.plot(self.get_domain(), data, marker='.')
        return plot

    def save_fig(self):
        plt.savefig(join(self.output_dir, f"{self.id}-{self.domain.time[self.t_index]:.2f}s.png"))

    def title(self):
        return f"{self.quantity} - {self.id} - {self.domain.time[self.t_index]:.2f}s"
    
    def ylabel(self):
        return f"{self.quantity} ({getattr(self.units, f'{self.quantity}')})"

    def xlabel(self):
        return f"{self.axis} ({self.units.space})"

    def get_domain(self):
        return getattr(self.domain, self.axis)

    def get_axis(self):
        lines = self.settings.models.eddy_diffusion.monitor_locations.lines
        return lines[self.id].parallel_axis

    def animate(self, data: ndarray):
        fig = plt.figure()
        def init():
            return self.plot(data[0])
        def frame(i):
            return self.plot(data[i])
        anim = animation.FuncAnimation(fig,
                                       frame,
                                       frames=self.settings.time_samples,
                                       init_func=init)
        anim.save("line_test.mp4", fps=5)
    