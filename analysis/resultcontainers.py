from typing import Tuple

from container import Domain

from config import RIDTConfig
from config import Units


class ResultContainer:
    def __init__(self, setting: RIDTConfig, geometry: str, id: str, quantity: str):
        self.setting = setting
        self.geometry = geometry
        self.id = id
        self.quantity = quantity
        self.units = Units(setting)
        self.domain = Domain(setting)
    
    def same_geometry(self, other):
        if self.geometry != other.geometry:
            raise ValueError("You are comparing two different geometries.")
    
    @property
    def unit(self):
        return getattr(self.units, f"{self.quantity}")
    

class Maximum(ResultContainer):

    def __init__(self,
                 setting: RIDTConfig,
                 geometry: str,
                 id: str,
                 quantity: str,
                 index: Tuple[int],
                 value: float):
        super().__init__(setting, geometry, id, quantity)
        self.index = index
        self.value = value
    
    def __lt__(self, other):
        if not isinstance(other, Maximum):
            raise TypeError(
        f"< not supported between instances of {Maximum} and {type(other)}")
        self.same_geometry(other)
        return True if self.value < other.value else False
    
    @property
    def string(self):
        u = getattr(self.units, f"{self.quantity}")
        factor = getattr(self.units, f"{self.quantity}_factor")
        rv = str()
        if self.index:
            t, x, y, z = self.domain.values(self.geometry, self.id, self.index)
            rv += f"id: {self.id}\n"
            rv += f"time: {t:.2f}{self.units.time}\n"
            rv += f"x: {x:.2f}{self.units.space}\n"
            rv += f"y: {y:.2f}{self.units.space}\n"
            rv += f"z: {z:.2f}{self.units.space}\n"
            rv += f"value: {self.value / factor:.2e}{u}\n\n"
        else:
            rv += "None\n\n"
        return rv
    
    @property
    def header(self):
        rv = str()
        return [
            "id",
            f"time ({self.units.time})",
            f"x ({self.units.space})",
            f"y ({self.units.space})",
            f"z ({self.units.space})",
            f"value ({self.unit})"
        ]
    
    @property
    def row(self):
        factor = getattr(self.units, f"{self.quantity}_factor")
        if self.index:
            t, x, y, z = self.domain.values(self.geometry, self.id, self.index)
            return [self.id, t, x, y, z, self.value / factor]
        else:
            return [self.id, "None", "None", "None", "None"]
    
    @property
    def fname(self):
        return f"{self.geometry}_maximums.csv"

    @property
    def title(self):
        return "Maxima"

    @property
    def extreme_title(self):
        return f"Maxium value for {self.geometry}:"
    
    @property
    def valid(self):
        return True if self.index else False
    

class Exceedance(ResultContainer):


    def __init__(self,
                 setting: RIDTConfig,
                 geometry: str,
                 id: str,
                 quantity: str,
                 index: Tuple[int],
                 threshold: float):
        super().__init__(setting, geometry, id, quantity)
        self.threshold = threshold
        self.index = index
    
    def __lt__(self, other):
        if not isinstance(other, Exceedance):
            raise TypeError(
        f"< not supported between instances of {Exceedance} and {type(other)}")
        self.same_geometry(other)
        return True if self.index[0] < other.index[0] else False
    
    @property
    def string(self):
        rv = str()
        if self.index:
            t, x, y, z = self.domain.values(self.geometry, self.id, self.index)
            rv += f"id: {self.id}\n"
            rv += f"time: {t:.2f}{self.units.time}\n"
            rv += f"x: {x:.2f}{self.units.space}\n"
            rv += f"y: {y:.2f}{self.units.space}\n"
            rv += f"z: {z:.2f}{self.units.space}\n"
        else:
            rv += "None\n\n"
        return rv
    
    @property
    def header(self):
        rv = str()
        return [
            "id",
            f"time ({self.units.time})",
            f"x ({self.units.space})",
            f"y ({self.units.space})",
            f"z ({self.units.space})",
        ]

    @property
    def row(self):
        if self.index:
            t, x, y, z = self.domain.values(self.geometry, self.id, self.index)
            return [self.id, t, x, y, z]
        else:
            return [self.id, "None", "None", "None"]
    
    @property
    def fname(self):
        return f"{self.geometry}_exceeds_{self.threshold}{self.unit}.csv"

    @property
    def title(self):
        return "Threshold Exceedance"
    
    @property
    def extreme_title(self):
        return f"Minimum time to {self.threshold}{self.unit} for {self.geometry}:"
    
    @property
    def valid(self):
        return True if self.index else False

class PercentExceedance(ResultContainer):


    def __init__(self,
                 setting: RIDTConfig,
                 geometry: str,
                 id: str,
                 quantity: str,
                 index: int,
                 threshold: float,
                 percent: float):
        super().__init__(setting, geometry, id, quantity)
        self.threshold = threshold
        self.index = index
        self.percent = percent
    
    def __lt__(self, other):
        if not isinstance(other, PercentExceedance):
            raise TypeError(
        f"< not supported between instances of {PercentExceedance} and"\
        f" {type(other)}")
        self.same_geometry
        return True if self.index < other.index else False
    
    @property
    def string(self):
        rv = str()
        if self.index:
            t = self.domain.time[self.index]
            rv += f"id: {self.id}\n"
            rv += f"time: {t:.2f}{self.units.time}\n\n"
        else:
            rv += "None\n\n"
        return rv
    
    @property
    def header(self):
        return [
            "id",
            f"time ({self.units.time})",
        ]

    @property
    def row(self):
        if self.index:
            t = self.domain.time[self.index]
            return [self.id, t]
        else:
            return [self.id, "None"]
    
    @property
    def fname(self):
        return f"{self.geometry}_exceeds_{self.threshold}{self.unit}.csv"
    
    @property
    def title(self):
        return f"{self.percent}% Threshold Exceedance"

    @property
    def extreme_title(self):
        return f"Minimum time to {self.threshold}{self.unit} for "\
               f"{self.percent}% of domain for {self.geometry}:"

    @property
    def valid(self):
        return True if self.index else False

class MaxPercentExceedance(ResultContainer):

    def __init__(self,
                 setting: RIDTConfig,
                 geometry: str,
                 id: str,
                 quantity:str,
                 value: float,
                 index: int,
                 threshold: float):
        super().__init__(setting, geometry, id, quantity)
        self.threshold = threshold
        self.index = index
        self.value = value

    def __lt__(self, other):
        if not isinstance(other, MaxPercentExceedance):
            raise TypeError(
        f"< not supported between instances of {MaxPercentExceedance} and {type(other)}")
        self.same_geometry(other)
        return True if self.value < other.value else False
    
    @property
    def string(self):
        rv = str()
        if self.index:
            t = self.domain.time[self.index]
            rv += f"id: {self.id}\n"
            rv += f"time: {t:.2f}{self.units.time}\n"
            rv += f"value: {self.value}%\n\n"
        else:
            rv += "None\n\n"
        return rv
    
    @property
    def header(self):
        return [
            "id",
            f"time ({self.units.time})",
            f"value (%)"
        ]

    @property
    def row(self):
        if self.index:
            t = self.domain.time[self.index]
            return [self.id, t, self.value]
        else:
            return [self.id, "None", "None"]

    @property
    def fname(self):
        return f"{self.geometry}_max%_exceeds_{self.threshold}{self.unit}.csv"

    @property
    def title(self):
        return "Maximum % Threshold Exceedance"
    
    @property
    def extreme_title(self):
        return f"Maximum percentage exceeding {self.threshold}{self.unit} "\
               f"for {self.geometry}:"

    @property
    def valid(self):
        return True if self.index else False
