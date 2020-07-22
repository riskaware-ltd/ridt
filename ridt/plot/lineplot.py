import warnings

from os.path import join

from numpy import ndarray

from ridt.config import RIDTConfig
from ridt.config import Units

from ridt.container import Domain

import matplotlib.pyplot as plt


class LinePlot:
    """The class that generates line plots over some spatial domain.

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
    
    config : :class:`~.LinePlots`
        The line plots settings object.

    outdir: :obj:`str`
        The path to the output directory for the run.

    """

    def __init__(self, settings: RIDTConfig, output_dir: str, quantity: str):
        """The :class:`~.LinePlot` constructor.

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
        self.config = self.settings.models.eddy_diffusion.lines_plots

    def __call__(self, id: str, data: ndarray, max_val: float, t_index: int) -> None:
        """The call method used to plot some data.

        Parameters
        ----------
        id : :obj:`str`
            The id string of the plane being plotted.

        data : :class:`~numpy.ndarray`
            The array of values to be plot.

        max_val : :obj:`float`
            The maximum value over the whole time domain.

        t_index : :obj:`int`
            The time index of the current data array.

        """
        self.id = id
        self.t_index = t_index
        self.max_val = max_val
        self.axis = self.get_axis()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.plot(data)
            plt.tight_layout()
            self.save_fig()
            plt.close()

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

        plot = plt.plot(self.get_domain(), data, marker='.')
        return plot

    def save_fig(self):
        """Creates the formatted string file name and saves plot to disk.

        """
        plt.savefig(join(self.output_dir, f"{self.id}-{self.domain.time[self.t_index]:.2f}s.png"))

    def title(self):
        """Creates formatted title string for the current plot.

        Returns
        -------
        :obj:`str`
            The title string.

        """
        return f"{self.quantity} - {self.id} - {self.domain.time[self.t_index]:.2f}s"
    
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
            The x-axis label string.

        """
        return f"{self.axis} ({self.units.space})"

    def get_domain(self):
        """Extract the x-axis values from the :attr:`domain`

        Returns
        -------
        :obj:`Iterable`[:obj:`float`]
            The x-axis values.

        """
        return getattr(self.domain, self.axis)

    def get_axis(self):
        """Parse the x axis from the plane settings object.

        Returns
        -------
        :obj:`str`
            The axis for the plot x, y, z  

        """
        lines = self.settings.models.eddy_diffusion.monitor_locations.lines
        return lines[self.id].parallel_axis
