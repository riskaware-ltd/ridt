from os.path import join

from base import ComputationalSpace
from base import RIDTOSError

from config import IDMFConfig
from config import ConfigFileWriter

from .batchdatastore import BatchDataStore
from .directoryagent import DirectoryAgent
from .datastorewriter import DataStoreWriter
from .datastorecsvwriter import DataStoreCSVWriter


class BatchDataStoreWriter:

    def __init__(self,
                 settings: IDMFConfig,
                 data_store: BatchDataStore,
                 space: ComputationalSpace):
        self.settings = settings
        self.data_store = data_store
        self.space = space

    def write(self, outdir: str):
        dir_agent = DirectoryAgent(outdir, self.space.shape)
        if self.space.zero:
            store = self.data_store[self.settings]
            ConfigFileWriter(outdir, "config.json", self.settings.__source__)
            DataStoreWriter(self.settings, store, dir_agent, "concentration")
            DataStoreCSVWriter(self.settings, store, dir_agent, "concentration")
        else:
            ConfigFileWriter(outdir, "batch_config.json", self.settings.__source__)
            try:
                with open(join(outdir, "run_summary.txt"), "w") as f:
                    f.write(self.space.cout_summary())
            except OSError as e:
                RIDTOSError(e)
            for idx, setting in enumerate(self.space.space):
                dir_agent.create_root_dir(idx)
                store = self.data_store[setting]
                ConfigFileWriter(dir_agent.outdir, "config.json", setting.__source__)
                DataStoreWriter(setting, store, dir_agent, "concentration")
                DataStoreCSVWriter(setting, store, dir_agent, "concentration")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
