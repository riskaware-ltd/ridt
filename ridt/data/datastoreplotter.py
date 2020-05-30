import csv

from os.path import join

from numpy import save
from numpy import min
from numpy import max
from numpy import linspace

from ridt.plot import PointPlot
from ridt.plot import LinePlot
from ridt.plot import ContourPlot

from ridt.data import DirectoryAgent

from .datastore import DataStore

from ridt.config import RIDTConfig
from ridt.config import Units


class DataStorePlotter:

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

        units = Units(settings)
        factor = getattr(units, f"{quantity}_factor")

        for geometry, plotter in DataStorePlotter.geometries.items():
            config = getattr(settings.models.eddy_diffusion, f"{geometry}_plots")
            if not config.output: continue
            indices = self.spread(settings.time_samples, config.number)
            dir_agent.create_plot_dir(geometry, quantity)
            plotter = plotter(settings, dir_agent.pdir, quantity)
            for id, data in getattr(data_store, geometry).items():
                rescaled_data = data / factor
                max_val = max(rescaled_data)
                if geometry == "points":
                    plotter(id, rescaled_data)
                else:
                    for idx in indices:
                        plotter(id, rescaled_data[idx], max_val, idx)

    def spread(self, time_samples: int, number_of_plots: int):
        return [int(i) for i in linspace(0, time_samples - 1, number_of_plots)]
