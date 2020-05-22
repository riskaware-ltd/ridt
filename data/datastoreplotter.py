import csv

from os.path import join

from numpy import save
from numpy import min
from numpy import max

from plot import PointPlot
from plot import LinePlot
from plot import ContourPlot

from .datastore import DataStore

from config import IDMFConfig


class DataStorePlotter:

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def plot(self,
             data_store: DataStore,
             settings: IDMFConfig,
             plot_type: str) -> None:

        if settings.models.eddy_diffusion.point_plots.output \
                or settings.dispersion_model == "well_mixed":
            pp = PointPlot(settings, self.output_dir)
            for name, data in data_store.points.items():
                try:
                    pp(data, plot_type, name)
                except KeyError:
                    pp(data, plot_type)

        if settings.models.eddy_diffusion.line_plots.output:
            lp = LinePlot(settings, self.output_dir)
            for name, data in data_store.lines.items():
                line = settings.\
                    models.\
                    eddy_diffusion.\
                    monitor_locations.\
                    lines[name]

                min_value = min(data)
                max_value = max(data)

                lp(data, line, name, plot_type, min_value, max_value)

        if settings.models.eddy_diffusion.contour_plots.output:
            cp = ContourPlot(settings, self.output_dir)
            for name, data in data_store.planes.items():
                plane = settings. \
                        models. \
                        eddy_diffusion. \
                        monitor_locations. \
                        planes[name]

                min_value = min(data)
                max_value = max(data)

                cp(data, plane, name, plot_type, min_value, max_value)
        
        if data_store.domain is not None:
            save(self.path("domain"), data_store.domain)

    def path(self, name: str) -> str:
        return join(self.output_dir, name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
