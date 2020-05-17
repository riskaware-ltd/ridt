from numpy import cumsum
from numpy import ndarray

from config import IDMFConfig

from data import DataStore


class Exposure:

    def __new__(cls, *args, **kwargs):
        instance = super(Exposure, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.data_store
    
    def __init__(self, data_store: DataStore, delta_t: float):
        self.data_store = self.evaluate(data_store, delta_t)
    
    def compute(self, data: ndarray, delta_t: float):
        return cumsum(data, axis=0) * delta_t

    def evaluate(self, data_store: DataStore, delta_t: float):
        rv = DataStore()

        for point_name, data in data_store.points.items():
            rv.add_point_data(point_name, self.compute(data, delta_t))

        for line_name, data in data_store.lines.items():
            rv.add_line_data(line_name, self.compute(data, delta_t))

        for plane_name, data in data_store.planes.items():
            rv.add_plane_data(plane_name, self.compute(data, delta_t))
        
        rv.add_domain_data(self.compute(data_store.domain, delta_t))

        return rv
 