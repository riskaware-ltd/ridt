from os.path import join

from tqdm import tqdm

from ridt.base import ComputationalSpace

from ridt.config import RIDTConfig
from ridt.config import ConfigFileWriter

from .batchdatastore import BatchDataStore
from .directoryagent import DirectoryAgent
from .datastoreplotter import DataStorePlotter


class BatchDataStorePlotter:
    """A class which handles the plotting of a batch data store.

    Iterates through a :class:`~.BatchDataStore` instance and runs  the
    :class:`~.DataStorePlotter` on them.

    Attributes
    ----------
    settings : :class:`~.RIDTConfig`
        The settings for the run in question.

    space : :class:`~.ComputationalSpace`
        The :class:`~.ComputationalSpace` instance corresponding to the
        :attr:`settings` attribute.
    
    outdir: :obj:`str`
        The path to the output directory for the run.
    
    quantity: :obj:`str`
        The string id for the quantity stored in the data  store.

    data_store : :class:`~.BatchDataStore`
        The batch data store to be analysed.

    """
    def __init__(self,
                 settings: RIDTConfig,
                 data_store: BatchDataStore,
                 space: ComputationalSpace,
                 outdir: str,
                 quantity: str):
        """The :class:`~.BatchDataStorePlotter` class initialiser.

        Parameters
        ----------
        settings : :class:`~.RIDTConfig`
            The settings for the run in question.

        data_store : :class:`~.BatchDataStore`
            The batch data store to be analysed.

        space : :class:`~.ComputationalSpace`
            The :class:`~.ComputationalSpace` instance corresponding to the
            :attr:`settings` attribute.

        outdir : :obj:`str`
            The path to the output directory for the run.

        quantity : :obj:`str`
            The string id for the quantity stored in the data  store.

        """
        self.settings = settings
        self.data_store = data_store
        self.outdir = outdir
        self.space = space
        self.quantity = quantity
        print(f"Plotting {self.quantity} data...")
        self.plot()

    def plot(self) -> None:
        """The method that loops through the :class:`~.DataStore` instances

        and calls the :class:`~.DataStorePlotter` class on them. This method
        will create the relevant subdirectories for output if they do not
        already exist.

        Returns
        -------
        None

        """
        dir_agent = DirectoryAgent(self.outdir, self.space.shape)
        arg = lambda x: (dir_agent, self.data_store[x], x, self.quantity)

        if self.space.zero:
            DataStorePlotter(*arg(self.settings))
        else:
            for idx, setting in enumerate(self.space.space):
                count = f"{idx + 1}/{len(self.space)}"
                print(f"Plotting computational space element {count}")
                dir_agent.create_root_dir(idx)
                DataStorePlotter(*arg(setting))