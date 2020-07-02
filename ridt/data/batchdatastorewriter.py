from os.path import join

from tqdm import tqdm

from ridt.base import ComputationalSpace
from ridt.base import RIDTOSError

from ridt.config import RIDTConfig
from ridt.config import ConfigFileWriter

from .batchdatastore import BatchDataStore
from .directoryagent import DirectoryAgent
from .datastorewriter import DataStoreWriter
from .datastorecsvwriter import DataStoreCSVWriter

BF = '{l_bar}{bar:30}{r_bar}{bar:-10b}'

class BatchDataStoreWriter:
    """A class which handles the writing to disk of a batch data store.

    Iterates through a :class:`~.BatchDataStore` instance and runs  the
    :class:`~.ConfigFileWriter` on the settings instances, and the
    :class:`~.DataStoreWriter` and :class:`~.DataStoreCSVWriter` on their
    corresponding :class:`~.DataStore` instances.

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
        """The :class:`~.BatchDataStoreWriter` class initialiser.

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
        self.space = space
        self.outdir = outdir
        self.quantity = quantity
        self.write()

    def write(self):
        """The method that loops through the :class:`~.DataStore` instances

        and runs the :class:`~.ConfigFileWriter` on the settings instances, and
        the :class:`~.DataStoreWriter` and :class:`~.DataStoreCSVWriter` on
        their corresponding :class:`~.DataStore` instances. This method will
        create the relevant subdirectories for output if they do not already
        exist.

        Returns
        -------
        None

        """
        dir_agent = DirectoryAgent(self.outdir, self.space.shape)

        arg = lambda x: (x, self.data_store[x], dir_agent, self.quantity)
        carg = lambda x, s: (self.outdir, s, x.__source__)

        if self.space.zero:
            DataStoreWriter(*arg(self.settings))
            if self.settings.write_data_to_csv:
                DataStoreCSVWriter(*arg(self.settings))
        else:
            ConfigFileWriter(*carg(self.settings, "batch_config.json"))
            for idx, setting in enumerate(self.space.space):
                count = f"{idx + 1}/{len(self.space)}"
                print(f"Writing computational space element {count}")
                dir_agent.create_root_dir(idx)
                DataStoreWriter(*arg(setting))
                if setting.write_data_to_csv:
                    DataStoreCSVWriter(*arg(setting))
