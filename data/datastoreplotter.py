import csv

from os.path import join

from numpy import save
from numpy import min
from numpy import max

from plot import PointPlot
from plot import LinePlot
from plot import ContourPlot

from data import DirectoryAgent

from .datastore import DataStore

from config import IDMFConfig


class DataStorePlotter:

    def __init__(self,
                 dir_agent: DirectoryAgent,
                 data_store: DataStore,
                 settings: IDMFConfig,
                 quantity: str) -> None:

        plot_config = settings.models.eddy_diffusion
        if plot_config.point_plots.output:
            pp = PointPlot(settings, dir_agent.outdir)
            for id, data in data_store.points.items():
                pp(data, quantity, id, dir_agent)

        if plot_config.line_plots.output:
            lp = LinePlot(settings, dir_agent.outdir)
            lines = settings.models.eddy_diffusion.monitor_locations.lines
            for id, data in data_store.lines.items():
                max_value = max(data)
                lp(data, lines[id], id, quantity, max_value, dir_agent)

        if plot_config.contour_plots.output:
            cp = ContourPlot(settings, dir_agent.outdir)
            planes = settings.models.eddy_diffusion.monitor_locations.planes
            for id, data in data_store.planes.items():
                max_value = max(data)
                cp(data, planes[id], id, quantity, max_value, dir_agent)
