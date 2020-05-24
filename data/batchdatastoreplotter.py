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
        if self.space.zero:
            with DataStorePlotter(outdir) as p:
                p.plot(self.data_store[self.settings], self.settings)
        else:
            with open(join(outdir, "run_summary.txt"), "w") as f:
                f.write(self.space.cout_summary())
            with DirectoryAgent(outdir, self.space.shape) as da:
                for idx, setting in enumerate(self.space.space):
                    da.create_root_dir(idx)
                    with DataStorePlotter(da) as p:
                        p.plot(self.data_store[setting], self.settings)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
