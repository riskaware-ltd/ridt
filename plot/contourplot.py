from os.path import join

from numpy import ndarray
from numpy import log
from numpy import log10
from numpy import floor
from numpy import ceil 
from numpy import arange
from numpy import power
from numpy import linspace
from numpy import meshgrid
from numpy.ma import masked_where

from config import IDMFConfig
from config import Units 

from container import Domain

from matplotlib import cm, ticker
from matplotlib import colors

from matplotlib.ticker import LogLocator
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure


class ContourPlot:

    def __init__(self, settings: IDMFConfig, output_dir: str, quantity: str):
        self.settings = settings
        self.output_dir = output_dir
        self.units = Units(settings)
        self.domain = Domain(self.settings)
        self.quantity = quantity
        self.config = self.settings.models.eddy_diffusion.planes_plots

    def __call__(self, id: str, data: ndarray, max_val: float, t_index: int):
        self.id = id
        self.t_index = t_index
        self.max_val = max_val
        self.xaxis, self.yaxis = self.get_axes()
        self.figsize = self.get_figsize()
        self.plot(data)
        self.save_fig()
        plt.close()

    def plot(self, data: ndarray):

        figure(num=None, figsize=self.figsize, dpi=120, facecolor='w', edgecolor='k')

        plt.title(self.title())
        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())

        if self.config.scale == "logarithmic":
            levels = self.get_log_scale()
            plot = plt.contourf(
                self.get_xdomain(),
                self.get_ydomain(),
                data, 
                levels,
                extend="both",
                norm=colors.LogNorm(),
                cmap=cm.RdBu_r)
            plt.colorbar()
        else:
            levels = self.get_linear_scale()
            plot = plt.contourf(
                self.get_xdomain(),
                self.get_ydomain(),
                data, 
                levels,
                cmap=cm.RdBu_r)
            plt.colorbar()
        plt.tight_layout()

        return plot

    def save_fig(self):
        plt.savefig(join(self.output_dir, f"{self.id}-{self.domain.time[self.t_index]:.2f}s.png"))

    def title(self):
        return f"{self.quantity} - {self.id} - {self.domain.time[self.t_index]:.2f}s"
    
    def xlabel(self):
        return f"{self.xaxis} ({self.units.space})"

    def ylabel(self):
        return f"{self.yaxis} ({self.units.space})"

    def get_xdomain(self):
        return getattr(self.domain, self.xaxis)

    def get_ydomain(self):
        return getattr(self.domain, self.yaxis)
    
    def get_figsize(self):
        dim = self.settings.models.eddy_diffusion.dimensions
        aspect_ratio = getattr(dim, self.xaxis) / getattr(dim, self.yaxis)
        return (8 * aspect_ratio, 6)

    def get_axes(self):
        planes = self.settings.models.eddy_diffusion.monitor_locations.planes
        string = planes[self.id].axis
        return string[0], string[1]
    
    def get_log_scale(self):
        lev_exp = linspace(floor(log10(1e-10)-1), ceil(max(ceil(log10(self.max_val)), 1)), 10)
        return power(10, lev_exp)

    def get_linear_scale(self):
        return linspace(0, self.max_val, 10)

    def __get_ranges(self):
        x_range = getattr(self.domain, list(self.plane.axis)[0])
        y_range = getattr(self.domain, list(self.plane.axis)[1])
        return x_range, y_range
