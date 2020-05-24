from typing import Tuple

from container import Domain

from config import IDMFConfig
from config import Units


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
        units = Units(setting)
        u = getattr(units, self.quantity)
        rv = str()
        if self.index:
            t, x, y, z = domain.values(self.geometry, self.id, self.index)
            rv += f"id: {self.id}\n"
            rv += f"time: {t}{units.time}\n"
            rv += f"x: {x}{units.space}\n"
            rv += f"y: {y}{units.space}\n"
            rv += f"z: {z}{units.space}\n"
            rv += f"value: {self.value}{u}\n\n"
        else:
            rv += "None\n\n"
        return rv
    
    def header(self, setting: IDMFConfig):
        units = Units(setting)
        u = getattr(units, self.quantity)
        rv = str()
        return [
            "id",
            f"time ({units.time})",
            f"x ({units.space})",
            f"y ({units.space})",
            f"z ({units.space})",
            f"value ({u})"
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
        units = Units(setting)
        rv = str()
        if self.index:
            t, x, y, z = domain.values(self.geometry, self.id, self.index)
            rv += f"id: {self.id}\n"
            rv += f"time: {t}{units.time}\n"
            rv += f"x: {x}{units.space}\n"
            rv += f"y: {y}{units.space}\n"
            rv += f"z: {z}{units.space}\n"
        else:
            rv += "None\n\n"
        return rv
    
    def header(self, setting: IDMFConfig):
        units = Units(setting)
        rv = str()
        return [
            "id",
            f"time ({units.time})",
            f"x ({units.space})",
            f"y ({units.space})",
            f"z ({units.space})",
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
        units = Units(setting)
        rv = str()
        if self.index:
            t = domain.time[self.index]
            rv += f"id: {self.id}\n"
            rv += f"time: {t}{units.time}\n\n"
        else:
            rv += "None\n\n"
        return rv

    
    def header(self, setting: IDMFConfig):
        units = Units(setting)
        return [
            "id",
            f"time ({units.time})",
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
        units = Units(setting)
        rv = str()
        if self.index:
            t = domain.time[self.index]
            rv += f"id: {self.id}\n"
            rv += f"time: {t}{units.time}\n"
            rv += f"value: {self.value}%\n\n"
        else:
            rv += "None\n\n"
        return rv
    
    def header(self, setting: IDMFConfig):
        units = Units(setting)
        return [
            "id",
            f"time ({units.time})",
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
