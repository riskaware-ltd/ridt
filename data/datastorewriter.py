import csv

from os.path import join

from numpy import ndarray
from numpy import savetxt
from numpy import save

from container import Domain

from .datastore import DataStore

class DataStoreWriter:

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
    
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

