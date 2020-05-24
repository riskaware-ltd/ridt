from typing import Tuple

from container import Domain

from config import IDMFConfig


class ResultContainer:
    def __init__(self, geometry: str, id: str, quantity: str):
        self.geometry = geometry
        self.id = id
        self.quantity = quantity
    
    def same_geometry(self, other):
        if self.geometry != other.geometry:
            raise ValueError("You are comparing two different geometries.")
    

class Maximum(ResultContainer):
    def __init__(self, geometry: str, id: str, quantity: str, index: Tuple[int], value: float):
        super().__init__(geometry, id, quantity)
        self.index = index
        self.value = value
    
    def __lt__(self, other):
        if not isinstance(other, Maximum):
            raise TypeError(
        f"< not supported between instances of {Maximum} and {type(other)}")
        self.same_geometry(other)
        return True if self.value < other.value else False
    
    def string(self, setting: IDMFConfig, domain: Domain):
        unit = getattr(setting, f"{self.quantity}_units")
        time_unit = setting.time_units
        spatial_unit = setting.spatial_units
        rv = str()
        if self.index:
            t, x, y, z = domain.values(self.geometry, self.id, self.index)
            rv += f"id: {self.id}\n"
            rv += f"time: {t}{time_unit}\n"
            rv += f"x: {x}{spatial_unit}\n"
            rv += f"y: {y}{spatial_unit}\n"
            rv += f"z: {z}{spatial_unit}\n"
            rv += f"value: {self.value}{unit}\n\n"
        else:
            rv += "None\n\n"
        return rv
    
    def header(self, setting: IDMFConfig):
        time_unit = setting.time_units
        spatial_unit = setting.spatial_units
        unit = getattr(setting, f"{self.quantity}_units")
        return [
            "id",
            f"time ({time_unit})",
            f"x ({spatial_unit})",
            f"y ({spatial_unit})",
            f"z ({spatial_unit})",
            f"value ({unit})"
        ]
    
    def row(self, domain: Domain):
        if self.index:
            t, x, y, z = domain.values(self.geometry, self.id, self.index)
            return [self.id, t, x, y, z, self.value]
        else:
            return [self.id, "None", "None", "None", "None"]
    
    @property
    def valid(self):
        return True if self.index else False
    

class Exceedance(ResultContainer):
    def __init__(self, geometry: str, id: str, quantity: str, index: Tuple[int], threshold: float):
        super().__init__(geometry, id, quantity)
        self.threshold = threshold
        self.index = index
    
    def __lt__(self, other):
        if not isinstance(other, Exceedance):
            raise TypeError(
        f"< not supported between instances of {Exceedance} and {type(other)}")
        self.same_geometry(other)
        return True if self.index[0] < other.index[0] else False
    
    def string(self, setting: IDMFConfig, domain: Domain):
        time_unit = getattr(setting, f"time_units")
        spatial_unit = setting.spatial_units
        rv = str()
        if self.index:
            t, x, y, z = domain.values(self.geometry, self.id, self.index)
            rv += f"id: {self.id}\n"
            rv += f"time: {t}{time_unit}\n"
            rv += f"x: {x}{spatial_unit}\n"
            rv += f"y: {y}{spatial_unit}\n"
            rv += f"z: {z}{spatial_unit}\n"
        else:
            rv += "None\n\n"
        return rv
    
    def header(self, setting: IDMFConfig):
        time_unit = setting.time_units
        spatial_unit = setting.spatial_units
        return [
            "id",
            f"time ({time_unit})",
            f"x ({spatial_unit})",
            f"y ({spatial_unit})",
            f"z ({spatial_unit})",
        ]

    def row(self, domain: Domain):
        if self.index:
            t, x, y, z = domain.values(self.geometry, self.id, self.index)
            return [self.id, t, x, y, z]
        else:
            return [self.id, "None", "None", "None"]
    
    @property
    def valid(self):
        return True if self.index else False

class PercentExceedance(ResultContainer):

    def __init__(self, geometry: str, id: str, quantity: str, index: int, threshold: float):
        super().__init__(geometry, id, quantity)
        self.threshold = threshold
        self.index = index
    
    def __lt__(self, other):
        if not isinstance(other, PercentExceedance):
            raise TypeError(
        f"< not supported between instances of {PercentExceedance} and {type(other)}")
        self.same_geometry
        return True if self.index < other.index else False
    
    def string(self, setting: IDMFConfig, domain: Domain):
        time_unit = getattr(setting, f"time_units")
        spatial_unit = setting.spatial_units
        rv = str()
        if self.index:
            t = domain.time[self.index]
            rv += f"id: {self.id}\n"
            rv += f"time: {t}{time_unit}\n\n"
        else:
            rv += "None\n\n"
        return rv

    
    def header(self, setting: IDMFConfig):
        time_unit = setting.time_units
        return [
            "id",
            f"time ({time_unit})",
        ]

    def row(self, domain: Domain):
        if self.index:
            t = domain.time[self.index]
            return [self.id, t]
        else:
            return [self.id, "None"]

    @property
    def valid(self):
        return True if self.index else False

class MaxPercentExceedance(ResultContainer):
    def __init__(self, geometry: str, id: str, quantity: str, value: float, index: int, threshold: float):
        super().__init__(geometry, id, quantity)
        self.threshold = threshold
        self.index = index
        self.value = value

    def __lt__(self, other):
        if not isinstance(other, MaxPercentExceedance):
            raise TypeError(
        f"< not supported between instances of {MaxPercentExceedance} and {type(other)}")
        self.same_geometry(other)
        return True if self.value < other.value else False
    
    def string(self, setting: IDMFConfig, domain: Domain):
        time_unit = getattr(setting, f"time_units")
        spatial_unit = setting.spatial_units
        rv = str()
        if self.index:
            t = domain.time[self.index]
            rv += f"id: {self.id}\n"
            rv += f"time: {t}{time_unit}\n"
            rv += f"value: {self.value}%\n\n"
        else:
            rv += "None\n\n"
        return rv
    
    def header(self, setting: IDMFConfig):
        time_unit = setting.time_units
        return [
            "id",
            f"time ({time_unit})",
            f"value (%)"
        ]

    def row(self, domain: Domain):
        if self.index:
            t = domain.time[self.index]
            return [self.id, t, self.value]
        else:
            return [self.id, "None", "None"]

    @property
    def valid(self):
        return True if self.index else False
