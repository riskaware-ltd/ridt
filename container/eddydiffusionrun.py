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
from analysis import Exposure


BF = '{l_bar}{bar:30}{r_bar}{bar:-10b}'

geometries = []

class EddyDiffusionRun:

    def __init__(self, settings: IDMFConfig, output_dir: str):

        print("Preparing Eddy Diffusion run...")
        self.settings = settings
        self.output_dir = output_dir
        self.data_store = BatchDataStore()
        self.exposure_store = None
        self.space = self.prepare()
        print("Evaluating model over domain...")
        self.evaluate()
        print("Computing exposure...")
        self.compute_exposure()
        print("Writing data to disk... ")
        self.write()
        print("Producing plots... ")
        self.plot()
        print("Performing data ananlysis...")
        self.analyse()
        print("\n\n")

    @property
    def geometries(self):
        locations = self.settings.models.eddy_diffusion.monitor_locations
        return [g for g, e in locations.evaluate.items() if e]

    def prepare(self) -> ComputationalSpace:
        restrict = {"models": "eddy_diffusion"}
        return ComputationalSpace(self.settings, restrict)
    
    def evaluate(self):
        for setting in tqdm(self.space.space, bar_format=BF):
            self.run(setting)

    def run(self, setting: IDMFConfig):

        self.data_store.add_run(setting)

        domain = Domain(setting)
        solver = EddyDiffusion(setting)
        locations = setting.models.eddy_diffusion.monitor_locations

        for geometry in self.geometries:
            for name, item in getattr(locations, geometry).items():
                output = solver(*getattr(domain, geometry)(item), domain.time)
                self.data_store[setting].add(geometry, name, squeeze(output))
    
    def compute_exposure(self):
        self.exposure_store = Exposure(self.settings, self.data_store)

    def write(self):
        BatchDataStoreWriter(self.settings, self.data_store, self.space, self.output_dir, "concentration")
        BatchDataStoreWriter(self.settings, self.exposure_store, self.space, self.output_dir, "exposure")

    def plot(self):
        BatchDataStorePlotter(self.settings, self.data_store, self.space, self.output_dir, "concentration",)
        BatchDataStorePlotter(self.settings, self.exposure_store, self.space, self.output_dir, "exposure")

    def analyse(self):
        BatchDataStoreAnalyser(self.settings, self.data_store, self.space, self.output_dir, "concentration")
        BatchDataStoreAnalyser(self.settings, self.exposure_store, self.space, self.output_dir, "exposure")

