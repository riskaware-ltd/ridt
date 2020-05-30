import sys

from tqdm import tqdm

from os.path import join

from base import ComputationalSpace

from config import summary
from config import RIDTConfig
from config import Units

from data import BatchDataStore
from data import DirectoryAgent
from data import DataStore

from .datastoreanalyser import DataStoreAnalyser
from .resultswriter import ResultsWriter
from .exposure import Exposure
from .batchresultswriter import BatchResultsWriter

from pprint import pprint

BF = '{l_bar}{bar:30}{r_bar}{bar:-10b}'


class BatchDataStoreAnalyser:

    quantities = [
        "concentration",
        "exposure"
    ]

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
        self.settings = settings
        self.space = space
        self.outdir = outdir
        self.quantity = quantity
        self.dir_agent = DirectoryAgent(outdir, self.space.shape)
        self.data_store = data_store
        self.results = dict()
        print(f"Analysing {self.quantity}...")
        self.analyse()
    
    def analyse(self):
        if self.space.zero:
            store = self.data_store[self.settings]
            result = DataStoreAnalyser(self.settings, store, self.quantity)
            self.results[self.settings] = result
            ResultsWriter(self.settings, result, self.dir_agent, self.quantity)
        else:
            for setting, store in tqdm(self.data_store.items(), bar_format=BF):
                idx = self.space.linear_index(setting)
                self.dir_agent.create_root_dir(idx)
                result = DataStoreAnalyser(setting, store, self.quantity)
                self.results[setting] = result
                ResultsWriter(setting, result, self.dir_agent, self.quantity)
            BatchResultsWriter(self.settings, self.space, self.results, self.outdir, self.quantity)
