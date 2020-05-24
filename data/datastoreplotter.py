import csv

from os.path import join

from plot import PointPlot
from plot import LinePlot
from plot import ContourPlot

from data import DirectoryAgent

from .datastore import DataStore

from config import IDMFConfig


class DataStorePlotter:

    def __init__(self, dir_agent: DirectoryAgent):
        self.dir_agent = dir_agent

    def plot(self, data_store: DataStore, settings: IDMFConfig) -> None:
        if settings.models.eddy_diffusion.point_plots.output \
                or settings.dispersion_model == "well_mixed":
            pp = PointPlot(settings, self.dir_agent.outdir)
            for name, data in data_store.points.items():
                try:
                    point = settings.\
                            models.\
                            eddy_diffusion.\
                            monitor_locations.\
                            points[name]
                    pp(data, point)
                except KeyError:
                    pp(data)

        if settings.models.eddy_diffusion.line_plots.output:
            lp = LinePlot(settings, self.dir_agent.outdir)
            for name, data in data_store.lines.items():
                line = settings.\
                    models.\
                    eddy_diffusion.\
                    monitor_locations.\
                    lines[name]
                lp(data, line)

        if settings.models.eddy_diffusion.contour_plots.output:
            cp = ContourPlot(settings, self.dir_agent.outdir)
            for name, data in data_store.planes.items():
                plane = settings. \
                        models. \
                        eddy_diffusion. \
                        monitor_locations. \
                        planes[name]
                cp(data, plane)

    def path(self, name: str) -> str:
        return join(self.output_dir, name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
