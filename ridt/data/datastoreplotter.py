from tqdm import tqdm

from numpy import max
from numpy import linspace

from ridt.plot import PointPlot
from ridt.plot import LinePlot
from ridt.plot import ContourPlot

from ridt.data import DirectoryAgent

from .datastore import DataStore

from ridt.config import RIDTConfig
from ridt.config import Units

from ridt import bar_args


class DataStorePlotter:
    """The class which plots the requested data from a :class:`~.DataStore`.

    """

    geometries = {
        "points": PointPlot,
        "lines": LinePlot,
        "planes": ContourPlot
    }

    def __init__(self,
                 dir_agent: DirectoryAgent,
                 data_store: DataStore,
                 settings: RIDTConfig,
                 quantity: str) -> None:
        """The :class:`DataStorePlotter` constructor.

        Parameters
        ----------
        settings : :class:`~.RIDTConfig`
            The settings for the run in question.

        dir_agent : :class:`~.DirectoryAgent`
            The path to the output directory for the run.
        
        data_store : :class:`~.DataStore`
            The data store to be analysed.

        quantity: :obj:`str`
            The string id for the quantity stored in the data  store.

        """
        units = Units(settings)
        factor = getattr(units, f"{quantity}_factor")

        for geometry, plotter in DataStorePlotter.geometries.items():
            # Get the Plotter Settings object.
            config = getattr(settings.models.eddy_diffusion, f"{geometry}_plots")
            # Verify that plots are requested.
            if not config.output: continue
            print(f"Plotting {geometry} monitor locations...")
            # Generates the time indices to plot from the config object.
            try:
                indices = self.spread(settings.time_samples, config.number)
            except AttributeError:
                # This happens if it is a point.
                indices = None
            dir_agent.create_plot_dir(geometry, quantity)
            plotter = plotter(settings, dir_agent.pdir, quantity)
            # Loop over all items in this geometry class.
            for id, data in getattr(data_store, geometry).items():
                # Rescale data from SI units back into output units.
                rescaled_data = data / factor
                # Find the maximum value.
                max_val = max(rescaled_data)
                if geometry == "points":
                    plotter(id, rescaled_data)
                else:
                    # Loop over all requested time indices.
                    for idx in tqdm(indices, **bar_args):
                        plotter(id, rescaled_data[idx], max_val, idx)

    def spread(self, time_samples: int, number_of_plots: int):
        """Returns a spread of time indices over time domain.

        Parameters
        ----------
        time_samples : :obj:`int`
            The total number of time samples.

        number_of_plots : :obj:`int`
            The number of requested plots.

        Returns
        -------
        :obj:`List`[:obj:`float`]
            The time indices to be plotted.
        
        """
        if number_of_plots > time_samples:
            number_of_plots = time_samples
        return [int(i) for i in linspace(0, time_samples - 1, number_of_plots)]
