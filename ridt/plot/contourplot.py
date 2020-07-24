import warnings

from os.path import join

from numpy import ndarray
from numpy import log10
from numpy import floor
from numpy import ceil 
from numpy import power
from numpy import linspace
from numpy import transpose

from ridt.config import RIDTConfig
from ridt.config import Units 

from ridt.container import Domain

from matplotlib import cm, ticker
from matplotlib import colors

from matplotlib.ticker import LogFormatter
from matplotlib.ticker import FormatStrFormatter
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure


class ContourPlot:
    """The class that generates contour plots.

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
    
    config : :class:`~.ContourPlots`
        The contour plots settings object.

    outdir: :obj:`str`
        The path to the output directory for the run.

    """
    def __init__(self, settings: RIDTConfig, output_dir: str, quantity: str):
        """The :class:`~.ContourPlot` constructor.

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
        self.config = self.settings.models.eddy_diffusion.planes_plots

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
        self.xaxis, self.yaxis = self.get_axes()
        self.figsize = self.get_figsize()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.plot(data)
        self.save_fig()
        plt.close()

    def plot(self, data: ndarray):
        """Calls various plotting functions.

        Parameters
        ----------
        data : :class:`~numpy.ndarray`
            The array of values to be plot.

        """

        figure(num=None, figsize=self.figsize, dpi=120, facecolor='w', edgecolor='k')

        plt.title(self.title())
        plt.xlabel(self.xlabel())
        plt.ylabel(self.ylabel())

        if self.config.scale == "logarithmic":
            levels = self.get_log_scale()
            kwargs = {"extend": "both", "norm": colors.LogNorm()}
        else:
            levels = self.get_linear_scale()
            kwargs = {}

        plt.contourf(
            self.get_xdomain(),
            self.get_ydomain(),
            transpose(data), 
            levels,
            cmap=cm.RdBu_r,
            **kwargs)

        if self.config.scale == "logarithmic":
            formatter = LogFormatter(10, labelOnlyBase=False, minor_thresholds=(1, 5))
            cb = plt.colorbar(ticks=self.get_log_scale(), format=formatter, )
            cb.ax.yaxis.set_major_formatter((FormatStrFormatter('%.2e')))
        else:
            plt.colorbar()

        plt.tight_layout()

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
        u = getattr(self.units, f'{self.quantity}')
        return f"{self.quantity} ({u}) - {self.id} - {self.domain.time[self.t_index]:.2f}s"
    
    def xlabel(self):
        """Creates the formatted x-axis label string.

        Returns
        -------
        :obj:`str`
            The x-axis label string.

        """
        return f"{self.xaxis} ({self.units.space})"

    def ylabel(self):
        """Creates the formatted y-axis label string.

        Returns
        -------
        :obj:`str`
            The y-axis label string.

        """
        return f"{self.yaxis} ({self.units.space})"

    def get_xdomain(self):
        """Extract the x-axis values from the :attr:`domain`

        Returns
        -------
        :obj:`Iterable`[:obj:`float`]
            The x-axis values.

        """
        return getattr(self.domain, self.xaxis)

    def get_ydomain(self):
        """Extract the x-axis values from the :attr:`domain`

        Returns
        -------
        :obj:`Iterable`[:obj:`float`]
            The x-axis values.

        """
        return getattr(self.domain, self.yaxis)
    
    def get_figsize(self):
        """Computes the aspect ratio for the plot.

        This is done relative the the physical bounds of the system.

        Returns
        -------
        :obj:`~.Tuple`[:obj:`float`]
            The width/height aspect ratio values.

        """
        dim = self.settings.dimensions
        aspect_ratio = getattr(dim, self.xaxis) / getattr(dim, self.yaxis)
        # 8 x 6 is the default values for the fig size in matplotlib.
        return (8 * aspect_ratio, 6)

    def get_axes(self):
        """Parse the x and y plot axes from the plane settings object.

        Returns
        -------
        :obj:`~.Tuple`[:obj:`str`]
            The two axes for the plot (x, y), (y, z), (x, z)

        """
        planes = self.settings.models.eddy_diffusion.monitor_locations.planes
        string = planes[self.id].axis
        return string[0], string[1]
    
    def get_log_scale(self):
        """Generate log scale values for the contours.

        This is either performed automatically or relative to defined values,
        depending on the user settings.

        Returns
        -------
        :obj:`Iterable`[:obj:`float`]
            The log scale values.
        
        """
        num_contour = self.config.number_of_contours    
        if self.config.range == "auto":
            min_contour = floor(log10(1e-20)-1)
            max_contour = ceil(log10(self.max_val))
        else:
            min_contour = floor(log10(self.config.contours.min))
            max_contour = ceil(log10(self.config.contours.max))
        levels = linspace(min_contour, max_contour, num_contour)
        return power(10, levels)

    def get_linear_scale(self):
        """Generate linear values for the contours.

        This is either performed automatically or relative to defined values,
        depending on the user settings.

        Returns
        -------
        :obj:`Iterable`[:obj:`float`]
            The linear scale values.
        
        """
        if self.config.range == "auto":
            min_contour = 0.0
            max_contour = self.max_val
        else:
            min_contour = self.config.contours.min
            max_contour = self.config.contours.max
        return linspace(min_contour, max_contour, self.config.number_of_contours)
