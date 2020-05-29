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
from analysis import Exposure

from container import Domain


BF = '{l_bar}{bar:30}{r_bar}{bar:-10b}'


class WellMixedRun:

    def __init__(self, settings: IDMFConfig, output_dir: str):
        print("Preparing Well Mixed run... ")
        self._settings = settings
        self._output_dir = output_dir
        self.data_store = BatchDataStore()
        self.exposure_store = None
        self.space = self.prepare()
        print("Evaluating model over domain... ")
        self.evaluate()
        print("Computing exposure...")
        self.compute_exposure()
        print("Writing data to disk... ")
        self.write()
        print("Producing plots... ")
        self.plot()
        print("\n")

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
    
    def compute_exposure(self):
        self.exposure_store = Exposure(self.settings, self.data_store)

    def write(self):
        BatchDataStoreWriter(self.settings, self.data_store, self.space, self.output_dir, "concentration")
        BatchDataStoreWriter(self.settings, self.exposure_store, self.space, self.output_dir, "exposure")

    def plot(self):
        BatchDataStorePlotter(self.settings, self.data_store, self.space, self.output_dir, "concentration",)
        BatchDataStorePlotter(self.settings, self.exposure_store, self.space, self.output_dir, "exposure")

    @property
    def settings(self):
        return self._settings

    @property
    def output_dir(self):
        return self._output_dir
