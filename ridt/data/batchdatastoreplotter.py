from os.path import join

from tqdm import tqdm

from ridt.base import ComputationalSpace

from ridt.config import RIDTConfig
from ridt.config import ConfigFileWriter

from .batchdatastore import BatchDataStore
from .directoryagent import DirectoryAgent
from .datastoreplotter import DataStorePlotter

BF = '{l_bar}{bar:30}{r_bar}{bar:-10b}'


class BatchDataStorePlotter:

    def __init__(self,
                 settings: RIDTConfig,
                 data_store: BatchDataStore,
                 space: ComputationalSpace,
                 outdir: str,
                 quantity: str):
        self.settings = settings
        self.data_store = data_store
        self.outdir = outdir
        self.space = space
        self.quantity = quantity
        print(f"Plotting {self.quantity} data...")
        self.plot()

    def plot(self):

        dir_agent = DirectoryAgent(self.outdir, self.space.shape)

        if self.space.zero:
            DataStorePlotter(dir_agent,
                             self.data_store[self.settings],
                             self.settings,
                             self.quantity)
        else:
            for idx, setting in tqdm(enumerate(self.space.space), total=len(self.space.space), bar_format=BF):
                dir_agent.create_root_dir(idx)
                DataStorePlotter(dir_agent,
                                 self.data_store[setting],
                                 setting,
                                 self.quantity)
