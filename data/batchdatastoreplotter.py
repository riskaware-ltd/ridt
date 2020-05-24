from os.path import join

from base import ComputationalSpace

from config import IDMFConfig
from config import ConfigFileWriter

from .batchdatastore import BatchDataStore
from .directoryagent import DirectoryAgent
from .datastoreplotter import DataStorePlotter


class BatchDataStorePlotter:

    def __init__(self,
                 settings: IDMFConfig,
                 data_store: BatchDataStore,
                 space: ComputationalSpace):
        self.settings = settings
        self.data_store = data_store
        self.space = space

    def plot(self, outdir: str):

        dir_agent = DirectoryAgent(outdir, self.space.shape)

        #### Tempory measure setting plot_type to concentration
        quantity = "concentration"
        #######################################################

        if self.space.zero:
            DataStorePlotter(dir_agent,
                             self.data_store[self.settings],
                             self.settings,
                             quantity)
        else:
            for idx, setting in enumerate(self.space.space):
                dir_agent.create_root_dir(idx)
                DataStorePlotter(dir_agent,
                                 self.data_store[setting],
                                 setting,
                                 quantity)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
