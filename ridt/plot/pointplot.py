import warnings

from os.path import join

from numpy import ndarray

from ridt.config import RIDTConfig
from ridt.config import Units

from ridt.container import Domain

import matplotlib.pyplot as plt
import matplotlib.dates as mdates 


def xfmt(x,pos=None):
    """custom date formatting"""
    x = mdates.num2date(x)
    label = x.strftime('%H:%M:%S')
    label = label.lstrip('0')
    return label


class PointPlot:
    """The class that generates line plots over time.

    Attributes
    ----------
    settings : :class:`~.RIDTConfig`
        The settings for the run in question.

    domain : :class:`~.Domain`
        The instance of :class:`~.Domain` corresponding to :attr:`setting`.

    units : :class:`~.Units`
        The instance of :class:`~.Units` corresponding to :attr:`setting`.
    
    quantity: :obj:`str`
        The string id for the quantity stored in the data  store.
    
    config : :class:`~.PointPlots`
        The point plots settings object.

    outdir: :obj:`str`
        The path to the output directory for the run.

    """
    def __init__(self, settings: RIDTConfig, output_dir: str, quantity: str):
        """The :class:`~.PointPlot` constructor.

        Parameters
        ----------
        settings : :class:`~.RIDTConfig`
            The settings for the run in question.

        outdir : :obj:`str`
            The path to the output directory for the run.

        quantity : :obj:`str`
            The string id for the quantity stored in the data  store.

        """
        self.settings = settings
        self.output_dir = output_dir
        self.units = Units(settings)
        self.domain = Domain(self.settings)
        self.quantity = quantity
        self.config = self.settings.models.eddy_diffusion.points_plots

    def __call__(self, id: str, data: ndarray):
        """The call method used to plot some data.

        Parameters
        ----------
        id : :obj:`str`
            The id string of the plane being plotted.

        data : :class:`~numpy.ndarray`
            The array of values to be plot.

        """
        self.id = id 
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.plot(data)
        plt.tight_layout()
        self.save_fig()
        plt.clf()

    def plot(self, data: ndarray):
        """Calls various plotting functions.

        Parameters
        ----------
        data : :class:`~numpy.ndarray`
            The array of values to be plot.

        """
        plt.title(self.title())
        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())
        if self.config.scale == "logarithmic":
            plt.yscale("log")
        plt.locator_params(nbins=10, axis='x')
        plot = plt.plot(self.convert_times(), data, marker='.')

        return plot

    def save_fig(self):
        """Creates the formatted string file name and saves plot to disk.

        """
        plt.savefig(join(self.output_dir, f"{self.id}.png"))

    def title(self):
        """Creates formatted title string for the current plot.

        Returns
        -------
        :obj:`str`
            The title string.

        """
        return f"{self.quantity} vs time - {self.id}"

    def ylabel(self):
        """Creates the formatted y-axis label string.

        Returns
        -------
        :obj:`str`
            The x-axis label string.

        """
        return f"{self.quantity} ({getattr(self.units, f'{self.quantity}')})"

    def xlabel(self):
        """Creates the formatted x-axis label string.

        Returns
        -------
        :obj:`str`
            The y-axis label string.

        """
        return f"Time ({self.config.time_axis_units}) [decimal fractions]"
    
    def convert_times(self):
        """Converts the time axis into date_time ticks

        Returns
        -------
        :obj:`list`[:obj:`str`]
            The times as datetime strings.

        """
        if self.config.time_axis_units == 's':
            return [t for t in self.domain.time]
        elif self.config.time_axis_units == 'm':
            return [t / 60 for t in self.domain.time]
        elif self.config.time_axis_units == 'h':
            return [t / 3600 for t in self.domain.time]
        