import csv

from itertools import product

from os import mkdir

from os.path import join

from numpy import ndarray
from numpy import savetxt
from numpy import save

from base import RIDTOSError

from config import RIDTConfig
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
                 setting: RIDTConfig,
                 data_store: DataStore,
                 dir_agent: DirectoryAgent,
                 quantity: str):
        self.dir_agent = dir_agent
        self.setting = setting
        self.units = Units(setting)
        self.domain = Domain(setting)
        self.quantity = quantity
        self.write(data_store)
    
    @property
    def geometries(self):
        locations = self.setting.models.eddy_diffusion.monitor_locations
        return [g for g, e in locations.evaluate.items() if e]

    def write(self, data_store: DataStore) -> None:
        for geometry in self.geometries:
            self.dir_agent.create_data_dir(geometry, self.quantity)
            for id in getattr(data_store, geometry):
                self.write_csv(geometry, id, data_store.get(geometry, id))
    
    def write_csv(self, geometry: str, id: str, data: ndarray):
        path = join(self.dir_agent.ddir, id + ".csv")
        factor = getattr(self.units, f"{self.quantity}_factor")

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
            f"value ({getattr(self.units, f'{self.quantity}')})"
        ])
        for index in product(*[range(i) for i in data.shape]):
            values = self.domain.values(geometry, id, index)
            writer.writerow(list(values) + [data[index] / factor])
        f.close()