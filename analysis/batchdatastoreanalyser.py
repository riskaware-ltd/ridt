import sys

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
                 outdir: str):
        self.settings = settings
        self.units = Units(settings)
        self.space = space
        self.dir_agent = DirectoryAgent(outdir, self.space.shape)

        self.concentration_store = data_store
        self.exposure_store = Exposure(self.settings, data_store)

        self.concentration_results = dict()
        self.exposure_results = dict()
        
        for quantity in BatchDataStoreAnalyser.quantities:
            if self.space.zero:
                q_store = getattr(self, f"{quantity}_store")[self.settings]
                self.analyse_store(self.settings, q_store, quantity)
            else:
                q_store = getattr(self, f"{quantity}_store")
                for setting, store in q_store.items():
                    idx = self.space.linear_index(setting)
                    self.dir_agent.create_root_dir(idx)
                    self.analyse_store(setting, store, quantity)
                q_res = getattr(self, f"{quantity}_results")
                BatchResultsWriter(self.settings, self.space, q_res, outdir, quantity)
        
    def analyse_store(self,
                      setting: IDMFConfig,
                      data_store: DataStore,
                      quantity: str):
        result = DataStoreAnalyser(setting, data_store, quantity)
        getattr(self, f"{quantity}_results")[setting] = result
        ResultsWriter(setting, result, self.dir_agent, quantity)

