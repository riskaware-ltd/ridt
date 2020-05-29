from typing import Iterable

from .idmfconfig import IDMFConfig

R = 8.3145 # Universal Gas Constant


class Units:
    def __init__(self, setting: IDMFConfig):
        self.time = setting.time_units
        self.mass = setting.mass_units
        self.concentration = setting.concentration_units
        self.exposure = setting.exposure_units
        self.space = setting.spatial_units
        self.concentration_si = "kg.m-3"
        self.exposure_si = "kg.s.m-3"
        self.temperature = setting.physical_properties.temperature
        self.pressure = setting.physical_properties.pressure
        self.molecular_weight = setting.physical_properties.agent_molecular_weight
        self.nmol = self.pressure / (self.temperature * R)

    @property
    def concentration_factor(self):
        if self.concentration == "kg.m-3":
            return 1.0
        elif self.concentration == "g.m-3":
            return 1e-3
        elif self.concentration == "mg.m-3":
            return 1e-6
        elif self.concentration == "ppm":
            return (self.molecular_weight * self.nmol) * 1e-6
        elif self.concentration == "ppb":
            return (self.molecular_weight * self.nmol) * 1e-9
        elif self.concentration == "ppt":
            return (self.molecular_weight * self.nmol) * 1e-12
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
    
