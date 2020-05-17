from os.path import join

from tqdm import tqdm

from numpy import zeros
from numpy import meshgrid
from numpy import squeeze 

from base import ComputationalSpace

from config import IDMFConfig

from equation import EddyDiffusion

from data import BatchDataStore
from data import BatchDataStoreWriter
from data import BatchDataStorePlotter

from container import Domain

from analysis import BatchDataStoreAnalyser


BF = '{l_bar}{bar:30}{r_bar}{bar:-10b}'


class EddyDiffusionRun:

    def __init__(self, settings: IDMFConfig, output_dir: str):

        self._settings = settings
        self._output_dir = output_dir
        self.data_store = BatchDataStore()
        self.space = self.prepare()
        self.evaluate()
        self.write()
        self.plot()
        self.analyse()

    def prepare(self) -> ComputationalSpace:
        restrict = {"models": self.settings.dispersion_model}
        return ComputationalSpace(self.settings, restrict)
    
    def evaluate(self):
        for setting in tqdm(self.space.space, bar_format=BF):
            self.run(setting)

    def run(self, setting: IDMFConfig):

        self.data_store.add_run(setting)
        domain = Domain(setting)
        solver = EddyDiffusion(setting)

        points = setting.models.eddy_diffusion.monitor_locations.points
        lines = setting.models.eddy_diffusion.monitor_locations.lines
        planes = setting.models.eddy_diffusion.monitor_locations.planes

        for point_name, point in points.items():
            output = solver(*domain.point(point), domain.time)
            self.data_store[setting].add_point_data(point_name, squeeze(output))

        for line_name, line in lines.items():
            output = solver(*domain.line(line), domain.time)
            self.data_store[setting].add_line_data(line_name, squeeze(output))

        for plane_name, plane in planes.items():
            output = solver(*domain.plane(plane), domain.time)
            self.data_store[setting].add_plane_data(plane_name, squeeze(output))
        
        output = solver(*domain.full, domain.time)
        self.data_store[setting].add_domain_data(output)

    def write(self):
        with BatchDataStoreWriter(self.settings,
                                  self.data_store,
                                  self.space) as dsw:
            dsw.write(self.output_dir)

    def plot(self):
        with BatchDataStorePlotter(self.settings,
                                   self.data_store,
                                   self.space) as dsp:
            dsp.plot(self.output_dir)
        pass

    def analyse(self):

        b = BatchDataStoreAnalyser(self.settings,
                               self.data_store,
                               self.space)
        b.write(self.output_dir)


    @property
    def settings(self):
        return self._settings
   
    @property
    def output_dir(self):
        return self._output_dir
