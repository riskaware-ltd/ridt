from itertools import product

from numpy import zeros
from numpy import array
from numpy import ndarray
from numpy.linalg import norm  

from config import RIDTConfig
from container import Domain


class UncertaintyMask:

    def __init__(self, setting: RIDTConfig):
        self.setting = setting
        self.sources = self.get_source_locations()
        self.domain = Domain(setting)

    def get_source_locations(self):
        rv = list()
        modes = ["instantaneous", "infinite_duration", "fixed_duration"]
        for mode in modes:
            sources = getattr(self.setting.modes, mode).sources
            rv += [array((s.x, s.y, s.z)) for s in sources.values()]
        return rv

    def mask(self, geometry: str, id: str, data: ndarray):
        rv = zeros(shape=data.shape)
        for index in product(*[range(i) for i in data.shape]):
            t, x, y, z = self.domain.values(geometry, id, index)
            p = array((x, y, z))
            for s in self.sources:
                if norm(s - p) <= 2.0:
                    rv[index] = 0.0
                else:
                    rv[index] = data[index]
        return rv
