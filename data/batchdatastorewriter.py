from os.path import join

from base import ComputationalSpace

from config import IDMFConfig
from config import ConfigFileWriter

from .batchdatastore import BatchDataStore
from .directoryagent import DirectoryAgent
from .datastorewriter import DataStoreWriter


class BatchDataStoreWriter:

    def __init__(self,
                 settings: IDMFConfig,
                 data_store: BatchDataStore,
                 space: ComputationalSpace):
        self.settings = settings
        self.data_store = data_store
        self.space = space

    def write(self, outdir: str):
        if self.space.zero:
            ConfigFileWriter(outdir, "config.json", self.settings.__source__)
            DataStoreWriter(self.settings, self.data_store[self.settings], outdir)
        else:
            ConfigFileWriter(outdir, "batch_config.json", self.settings.__source__)
            with open(join(outdir, "run_summary.txt"), "w") as f:
                f.write(self.space.cout_summary())
            with DirectoryAgent(outdir, self.space.shape) as da:
                for idx, setting in enumerate(self.space.space):
                    da.create_rundir(idx)
                    path = da.build_rundir_path(idx)
                    ConfigFileWriter(path, "config.json", setting.__source__)
                    DataStoreWriter(setting, self.data_store[setting], path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
