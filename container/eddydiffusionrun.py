from tqdm import tqdm

from numpy import zeros
from numpy import meshgrid
from numpy import squeeze 

from config.idmfconfig import IDMFConfig
from base.settings import ComputationalSpace
from data.datastore import DataStore
from container.domain import Domain

from equation import EddyDiffusion
from analysis import PointPlot
from analysis import LinePlot
from analysis import ContourPlot

BF = '{l_bar}{bar:30}{r_bar}{bar:-10b}'


class EddyDiffusionRun:

    def __init__(self, settings: IDMFConfig, output_dir: str):

        self._settings = settings
        self._output_dir = output_dir
        self.data_store = DataStore()
        self.space = self.prepare()
        self.evaluate()

    def prepare(self) -> ComputationalSpace:
        restrict = {"models": self.settings.dispersion_model}
        return ComputationalSpace(self.settings, restrict)
    
    def evaluate(self):
        for setting in tqdm(self.space.configuration_space, bar_format=BF):
            self.run(setting)

    def run(self, setting: IDMFConfig):

        domain = Domain(setting)
        solver = EddyDiffusion(setting)

        points = setting.models.eddy_diffusion.monitor_locations.points
        lines = setting.models.eddy_diffusion.monitor_locations.lines
        planes = setting.models.eddy_diffusion.monitor_locations.planes

        for point_name, point in points.items():
            output = solver(*domain.point(point), self.time)
            self.data_store.add_point_data(setting, point_name, squeeze(output))

        for line_name, line in lines.items():
            output = solver(*domain.line(line), self.time)
            self.data_store.add_line_data(setting, line_name, squeeze(output))

        for plane_name, plane in planes.items():
            output = solver(*domain.plane(plane), self.time)
            self.data_store.add_plane_data(setting, plane_name, squeeze(output))
        
        output = solver(self._X, self._Y, self._Z, self.time)
        self.data_store.add_domain_data(setting, output)

    @property
    def settings(self):
        return self._settings
   
    @property
    def output_dir(self):
        return self._output_dir
   