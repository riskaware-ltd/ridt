from typing import Union

from numpy import cumsum
from numpy import ndarray

from config import IDMFConfig

from data import DataStore
from data import BatchDataStore

class Exposure:

    def __new__(cls, *args, **kwargs):
        instance = super(Exposure, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.data_store
    
    def __init__(self, setting: IDMFConfig, data_store: Union[DataStore, BatchDataStore]):
        self.setting = setting
        self.delta_t = self.setting.total_time / self.setting.time_samples
        self.data_store = self.evaluate(data_store)
    
    def compute(self, data: ndarray):
        return cumsum(data, axis=0) * self.delta_t

    def evaluate(self, data_store: DataStore):
        if isinstance(data_store, DataStore):
            rv = DataStore()
            for geometry in rv.geometries:
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
    