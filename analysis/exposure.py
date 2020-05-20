from numpy import cumsum
from numpy import ndarray

from config import IDMFConfig

from data import DataStore


class Exposure:

    def __new__(cls, *args, **kwargs):
        instance = super(Exposure, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.data_store
    
    def __init__(self, setting: IDMFConfig, data_store: DataStore):
        self.setting = setting
        self.delta_t = self.setting.total_time / self.setting.time_samples
        self.data_store = self.evaluate(data_store)
    
    def compute(self, data: ndarray):
        return cumsum(data, axis=0) * self.delta_t

    def evaluate(self, data_store: DataStore):
        rv = DataStore()

        for point_name, data in data_store.points.items():
            rv.add_point_data(point_name, self.compute(data, delta_t))

        for line_name, data in data_store.lines.items():
            rv.add_line_data(line_name, self.compute(data, delta_t))

        for plane_name, data in data_store.planes.items():
            rv.add_plane_data(plane_name, self.compute(data, delta_t))
        
        rv.add_domain_data(self.compute(data_store.domain, delta_t))

        return rv
 