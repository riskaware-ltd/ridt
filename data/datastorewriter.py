import csv

from os.path import join

from numpy import ndarray
from numpy import savetxt
from numpy import save

from config import IDMFConfig

from .datastore import DataStore

class DataStoreWriter:

    def __new__(cls, *args, **kwargs):
        instance = super(DataStoreWriter, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance

    def __init__(self, setting: IDMFConfig, data_store: DataStore, output_dir: str):
        self.output_dir = output_dir
        self.setting = setting
        self.write(data_store)
    
    def write(self, data_store: DataStore) -> None:
        for name, data in data_store.points.items():
            save(self.path(name), data)
    
        for name, data in data_store.lines.items():
            save(self.path(name), data)

        for name, data in data_store.planes.items():
            save(self.path(name), data)
        
        if data_store.domain is not None:
            save(self.path("domain"), data_store.domain)

    def path(self, name: str) -> str:
        return join(self.output_dir, name)
