
from .idmfconfig import IDMFConfig


class Units:
    def __init__(self, setting: IDMFConfig):
        self.time = setting.time_units
        self.concentration = setting.concentration_units
        self.exposure = setting.exposure_units
        self.space = setting.spatial_units
