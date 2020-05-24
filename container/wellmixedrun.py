from os.path import join

from tqdm import tqdm

from numpy import zeros
from numpy import meshgrid
from numpy import linspace

from base import ComputationalSpace
from equation import WellMixed

from config import IDMFConfig

from data import BatchDataStore
from data import BatchDataStoreWriter
from data import BatchDataStorePlotter
from analysis import BatchDataStoreAnalyser

from container import Domain


BF = '{l_bar}{bar:30}{r_bar}{bar:-10b}'


class WellMixedRun:

    def __init__(self, settings: IDMFConfig, output_dir: str):
        self._settings = settings
        self._output_dir = output_dir
        self.data_store = BatchDataStore()
        self.space = self.prepare()
        self.evaluate()
        self.write()
        self.plot()
        self.analyse()

    def prepare(self):
        restrict = {"models": "well_mixed"}
        return ComputationalSpace(self.settings, restrict)
    
    def evaluate(self):
        for setting in tqdm(self.space.space, bar_format=BF):
            self.run(setting)

    def run(self, setting: IDMFConfig):
        self.data_store.add_run(setting)
        domain = Domain(setting)
        solver = WellMixed(setting)
        output = solver(domain.time)
        self.data_store[setting].add("points", "well_mixed", output)

    def write(self):
        with BatchDataStoreWriter(self.settings, self.data_store, self.space) as dsw:
            dsw.write(self.output_dir)

    def plot(self):
        with BatchDataStorePlotter(self.settings, self.data_store, self.space) as dsp:
            dsp.plot(self.output_dir)
        pass

    def analyse(self):
        BatchDataStoreAnalyser(self.settings, self.data_store, self.space, self.output_dir)

    @property
    def settings(self):
        return self._settings

    @property
    def output_dir(self):
        return self._output_dir
