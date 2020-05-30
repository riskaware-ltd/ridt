from typing import Union

from numpy import cumsum
from scipy.integrate import cumtrapz
from numpy import ndarray

from ridt.config import RIDTConfig

from ridt.data import DataStore
from ridt.data import BatchDataStore

class Exposure:

    def __new__(cls, *args, **kwargs):
        instance = super(Exposure, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.data_store
    
    def __init__(self, setting: RIDTConfig, data_store: Union[DataStore, BatchDataStore]):
        self.setting = setting
        self.delta_t = self.setting.total_time / self.setting.time_samples
        self.data_store = self.evaluate(data_store)
    
    @property
    def geometries(self):
        locations = self.setting.models.eddy_diffusion.monitor_locations
        return [g for g, e in locations.evaluate.items() if e]

    def compute(self, data: ndarray):
        return cumtrapz(data, dx=self.delta_t, axis=0, initial=0)

    def evaluate(self, data_store: DataStore):
        if isinstance(data_store, DataStore):
            rv = DataStore()
            for geometry in self.geometries:
                for name, data in getattr(data_store, geometry).items():
                    rv.add(geometry, name, self.compute(data))
            return rv
        elif isinstance(data_store, BatchDataStore):
            rv = BatchDataStore()
            for setting, store in data_store.items():
                rv.add_run(setting)
                rv[setting] = self.evaluate(data_store[setting])
            return rv
        else:
            raise TypeError(f"Expecting {DataStore} or {BatchDataStore}.")
    