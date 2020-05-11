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

    def plot(self, outdir: str, time: int):
        if self.space.zero:
            with ConfigFileWriter(outdir) as cfw:
                cfw("config.json", self.settings.__source__)
            with DataStorePlotter(outdir) as w:
                w.plot(self.data_store[self.settings], self.settings, time)
        else:
            with ConfigFileWriter(outdir) as cfw:
                cfw("batch_config.json", self.settings.__source__)
            with open(join(outdir, "run_summary.txt"), "w") as f:
                f.write(self.space.cout_summary())
            with DirectoryAgent(outdir, self.space.shape) as da:
                for idx, setting in enumerate(self.space.space):
                    da.create_rundir(idx)
                    with ConfigFileWriter(da.build_rundir_path(idx)) as cfw:
                        cfw("config.json", setting.__source__)
                    with DataStorePlotter(da.build_rundir_path(idx)) as w:
                        w.plot(self.data_store[setting], self.settings, time)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
