from tqdm import tqdm

from numpy import zeros
from numpy import meshgrid
from numpy import linspace

from config.idmfconfig import IDMFConfig
from data.datastore import DataStore
from container.domain import Domain
from base.settings import ComputationalSpace

from equation import WellMixed
from analysis import PointPlot

BF = '{l_bar}{bar:30}{r_bar}{bar:-10b}'


class WellMixedRun:

    def __init__(self, settings: IDMFConfig, output_dir: str):
        self._settings = settings
        self._output_dir = output_dir
        self.data_store = DataStore()
        self.space = self.prepare()
        self.evaluate()

    def prepare(self):
        restrict = {"models": self.settings.dispersion_model}
        return ComputationalSpace(self.settings, restrict)
    
    def evaluate(self):
        for setting in tqdm(self.space.configuration_space, bar_format=BF):
            self.run(setting)

    def run(self, setting: IDMFConfig):
        domain = Domain
        solver = WellMixed(settings)
        output = solver(self.time)
        self.data_store.add_point_data(setting, output)

    @property
    def settings(self):
        return self._settings

    @property
    def output_dir(self):
        return self._output_dir

    @property
    def time(self):
        return self._time

