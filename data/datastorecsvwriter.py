import csv

from itertools import product

from os import mkdir

from os.path import join

from numpy import ndarray
from numpy import savetxt
from numpy import save

from base import RIDTOSError

from config import IDMFConfig
from config import Units

from .directoryagent import DirectoryAgent

from container import Domain

from .datastore import DataStore

class DataStoreCSVWriter:

    def __new__(cls, *args, **kwargs):
        instance = super(DataStoreCSVWriter, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance

    def __init__(self,
                 setting: IDMFConfig,
                 data_store: DataStore,
                 dir_agent: DirectoryAgent,
                 quantity: str):
        self.dir_agent = dir_agent
        self.setting = setting
        self.units = Units(setting)
        self.domain = Domain(setting)
        self.quantity = quantity
        self.write(data_store)
    
    def write(self, data_store: DataStore) -> None:
        for geometry in data_store.geometries:
            self.dir_agent.create_quantity_dir(geometry, self.quantity)
            for id in getattr(data_store, geometry):
                self.write_csv(geometry, id, data_store.get(geometry, id))
    
    def write_csv(self, geometry: str, id: str, data: ndarray):
        qu = getattr(self.units, f"{self.quantity}_si")

        path = join(self.dir_agent.qdir, id + ".csv")

        try:
            f = open(path, 'w', newline="")
        except OSError as e:
            raise RIDTOSError(e)

        writer = csv.writer(f, delimiter=",")
        writer.writerow([
            f"time ({self.units.time})",
            f"x ({self.units.space})",
            f"y ({self.units.space})",
            f"z ({self.units.space})",
            f"value ({qu})"
        ])
        for index in product(*[range(i) for i in data.shape]):
            values = self.domain.values(geometry, id, index)
            writer.writerow(list(values) + [data[index]])
        f.close()