import csv

from os import mkdir

from os.path import join

from numpy import ndarray
from numpy import savetxt
from numpy import save

from config import IDMFConfig

from .directoryagent import DirectoryAgent

from .datastore import DataStore

class DataStoreWriter:

    def __new__(cls, *args, **kwargs):
        instance = super(DataStoreWriter, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance

    def __init__(self,
                 setting: IDMFConfig,
                 data_store: DataStore,
                 dir_agent: DirectoryAgent,
                 quantity: str):
        self.dir_agent = dir_agent
        self.setting = setting
        self.quantity = quantity
        self.write(data_store)
    
    def write(self, data_store: DataStore) -> None:
        for geometry in data_store.geometries:
            self.dir_agent.create_data_dir(geometry, self.quantity)
            for id in getattr(data_store, geometry):
                save(join(self.dir_agent.ddir, id), data_store.get(geometry, id))
