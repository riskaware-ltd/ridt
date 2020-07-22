from ridt.base import ComputationalSpace

from ridt.config import RIDTConfig

from ridt.data import BatchDataStore
from ridt.data import DirectoryAgent
from ridt.data import DataStore

from .datastoreanalyser import DataStoreAnalyser
from .resultswriter import ResultsWriter
from .batchresultswriter import BatchResultsWriter

BF = '{l_bar}{bar:30}{r_bar}{bar:-10b}'


class BatchDataStoreAnalyser:
    """Batch data store analyser class.

    Iterates through a :class:`~.BatchDataStore` instance and runs  the
    :class:`~.DataStoreAnalyser` and :class:`~.ResultsWriter` classes on them.

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
    
    dir_agent: :class:`~.DirectoryAgent`
        The  :class:`~.DirectoryAgent` instance for this run.
    
    results : :obj:`dict` [:class:`~.RIDTConfig`, :class:`~.DataStoreAnalyser`]
        A dictionary of :class:`~.DataStoreAnalyser` instances for each
        :class:`~.RIDTConfig` object in :attr:`space`.

    """
    def __new__(cls, *args, **kwargs):
        instance = super(BatchDataStoreAnalyser, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return None

    def __init__(self,
                 settings: RIDTConfig,
                 data_store: BatchDataStore,
                 space: ComputationalSpace,
                 outdir: str,
                 quantity: str):
        """The :class:`~.BatchDataStoreAnalyser` class initialiser.

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
        self.space = space
        self.outdir = outdir
        self.quantity = quantity
        self.dir_agent = DirectoryAgent(outdir, self.space.shape)
        self.data_store = data_store
        self.results = dict()
        print(f"Analysing {self.quantity}...")
        self.analyse()
    
    def analyse(self) -> None:
        """The method that loops through the :class:`~.DataStore` instances

        and calls the :class:`~.DataStoreAnalyser` and :class:`~.ResultsWriter`
        classes on them. This method will create the relevant subdirectories
        for output if they do not already exist.

        Returns
        -------
        None
    
        """
        if self.space.zero:
            store = self.data_store[self.settings]
            result = DataStoreAnalyser(self.settings, store, self.quantity)
            self.results[self.settings] = result
            ResultsWriter(self.settings, result, self.dir_agent, self.quantity)
        else:
            for setting, store in self.data_store.items():
                idx = self.space.linear_index(setting)
                print(f"Analysing computational space element {idx + 1}/{len(self.space)}")
                self.dir_agent.create_root_dir(idx)
                result = DataStoreAnalyser(setting, store, self.quantity)
                self.results[setting] = result
                ResultsWriter(setting, result, self.dir_agent, self.quantity)
            BatchResultsWriter(self.settings, self.space, self.results, self.outdir, self.quantity)
