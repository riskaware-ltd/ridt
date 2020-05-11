import csv

from os.path import join

from numpy import ndarray
from numpy import savetxt
from numpy import save

from container import Domain

from plot import PointPlot
from plot import LinePlot
from plot import ContourPlot

from .datastore import DataStore

from config import IDMFConfig


class DataStorePlotter:

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def plot(self, data_store: DataStore, settings: IDMFConfig, time: int) -> None:
        pp = PointPlot(settings, self.output_dir)
        for name, data in data_store.points.items():
            point = settings.\
                    models.\
                    eddy_diffusion.\
                    monitor_locations.\
                    points[name]
            pp(data, point)

        lp = LinePlot(settings, self.output_dir)
        for name, data in data_store.lines.items():
            line = settings.\
                   models.\
                   eddy_diffusion.\
                   monitor_locations.\
                   lines[name]
            lp(data, line, time)

        cp = ContourPlot(settings, self.output_dir)
        for name, data in data_store.planes.items():
            plane = settings. \
                    models. \
                    eddy_diffusion. \
                    monitor_locations. \
                    lines[name]
            cp(data, plane, time)
        
        if data_store.domain is not None:
            save(self.path("domain"), data_store.domain)

    def path(self, name: str) -> str:
        return join(self.output_dir, name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
