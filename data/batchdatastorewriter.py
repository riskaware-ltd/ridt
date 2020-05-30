from os.path import join

from tqdm import tqdm

from base import ComputationalSpace
from base import RIDTOSError

from config import RIDTConfig
from config import ConfigFileWriter

from .batchdatastore import BatchDataStore
from .directoryagent import DirectoryAgent
from .datastorewriter import DataStoreWriter
from .datastorecsvwriter import DataStoreCSVWriter

BF = '{l_bar}{bar:30}{r_bar}{bar:-10b}'

class BatchDataStoreWriter:

    def __init__(self,
                 settings: RIDTConfig,
                 data_store: BatchDataStore,
                 space: ComputationalSpace,
                 outdir: str,
                 quantity: str):
        self.settings = settings
        self.data_store = data_store
        self.space = space
        self.outdir = outdir
        self.quantity = quantity
        print(f"Writing {self.quantity} data...")
        self.write()

    def write(self):
        dir_agent = DirectoryAgent(self.outdir, self.space.shape)
        if self.space.zero:
            store = self.data_store[self.settings]
            ConfigFileWriter(self.outdir, "config.json", self.settings.__source__)
            DataStoreWriter(self.settings, store, dir_agent, self.quantity)
            DataStoreCSVWriter(self.settings, store, dir_agent, self.quantity)
        else:
            ConfigFileWriter(self.outdir, "batch_config.json", self.settings.__source__)
            for idx, setting in tqdm(enumerate(self.space.space), total=len(self.space.space), bar_format=BF):
                dir_agent.create_root_dir(idx)
                store = self.data_store[setting]
                ConfigFileWriter(dir_agent.outdir, self.quantity, setting.__source__)
                DataStoreWriter(setting, store, dir_agent, self.quantity)
                DataStoreCSVWriter(setting, store, dir_agent, self.quantity)
