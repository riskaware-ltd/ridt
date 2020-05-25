import sys

from tqdm import tqdm

from os.path import join

from base import ComputationalSpace

from config import summary
from config import IDMFConfig
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
                 settings: IDMFConfig,
                 data_store: BatchDataStore,
                 space: ComputationalSpace,
                 outdir: str,
                 quantity: str):
        self.settings = settings
        self.units = Units(settings)
        self.space = space
        self.quantity = quantity
        self.dir_agent = DirectoryAgent(outdir, self.space.shape)

        self.data_store = data_store
        self.results = dict()
    
        print(f"Analysing {self.quantity}...")
        if self.space.zero:
            store = self.data_store[self.settings]
            self.analyse_store(self.settings, store, quantity)
        else:
            for setting, store in tqdm(self.data_store.items(), bar_format=BF):
                idx = self.space.linear_index(setting)
                self.dir_agent.create_root_dir(idx)
                self.analyse_store(setting, store, quantity)
            BatchResultsWriter(self.settings, self.space, self.results, outdir, quantity)
        
    def analyse_store(self,
                      setting: IDMFConfig,
                      data_store: DataStore,
                      quantity: str):
        result = DataStoreAnalyser(setting, data_store, quantity)
        self.results[setting] = result
        ResultsWriter(setting, result, self.dir_agent, quantity)

