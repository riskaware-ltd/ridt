from typing import Iterable

from .idmfconfig import IDMFConfig


class Units:
    def __init__(self, setting: IDMFConfig):
        self.time = setting.time_units
        self.mass = setting.mass_units
        self.concentration = setting.concentration_units
        self.exposure = setting.exposure_units
        self.space = setting.spatial_units
        self.concentration_si = "kg.m-3"
        self.exposure_si = "kg.s.m-3"

    @property
    def concentration_factor(self):
        if self.concentration == "kg.m-3":
            return 1.0
        elif self.concentration == "g.m-3":
            return 1e-3
        elif self.concentration == "mg.m-3":
            return 1e-6
        elif self.concentration == "ppm":
            return 1e-3
        elif self.concentration == "ppb":
            return 1e-6
        elif self.concentration == "ppt":
            return 1e-9
        else:
            raise ValueError(f"{self.concentration} not a valid unit")

    @property
    def exposure_factor(self):
        if self.exposure == "kg.s.m-3":
            return 1.0
        elif self.exposure == "mg.min.m-3":
            return 1e-6 * 60
        else:
            raise ValueError(f"{self.exposure} not a valid unit")

    def concentration_converter(self, values: Iterable):
        return [v * self.concentration_factor for v in values]

    def exposure_converter(self, values: Iterable):
        return [v * self.exposure_factor for v in values]
    
