import sys

from numpy import ndarray
from numpy import any
from numpy import where
from numpy import max

from config import IDMFConfig

from container import Domain

from data import DataStore

from .exposure import Exposure


class DataStoreAnalyser:

    def __init__(self, setting: IDMFConfig, data_store: DataStore):
        self.setting = setting
        self.data_store = data_store
        self.domain = Domain(self.setting)
        self.delta_t = self.setting.total_time / self.setting.time_samples
        self.exposures = Exposure(data_store, self.delta_t)
        self.points = self.setting.models.eddy_diffusion.monitor_locations.points
        self.lines = self.setting.models.eddy_diffusion.monitor_locations.lines
        self.planes = self.setting.models.eddy_diffusion.monitor_locations.planes

    def max_exposure(self):
        value = 0.0
        name = ""
        for point_name, point in self.points.items():
            tmp = max(self.exposures.get_point_data(point_name))
            if tmp > value:
                value = tmp
                name = point_name

        for line_name, line in self.lines.items():
            tmp = max(self.exposures.get_line_data(line_name))
            if tmp > value:
                value = tmp
                name = line_name

        for plane_name, plane in self.planes.items():
            tmp = max(self.exposures.get_plane_data(plane_name))
            if tmp > value:
                value = tmp
                name = plane_name
        
        tmp = max(self.exposures.get_domain_data())
        if tmp > value:
            value = tmp
            name = "domain" 

        return name, value
        

    def exceeds_exposure(self, value: float):
        rv = Exceedance()

        for point_name, point in self.points.items():
            exceeds = where(self.exposures.get_point_data(point_name) > value)
            if any(exceeds):
                index = exceeds[0][0]
                rv.add_point(point_name, self.domain.time[index])

        for line_name, line in self.lines.items():
            exceeds = where(self.exposures.get_line_data(line_name) > value)
            if any(exceeds):
                index = exceeds[0][0]
                rv.add_line(line_name, self.domain.time[index])

        for plane_name, plane in self.planes.items():
            exceeds = where(self.exposures.get_plane_data(plane_name) > value)
            if any(exceeds):
                index = exceeds[0][0]
                rv.add_plane(plane_name, self.domain.time[index])
        
        exceeds = where(self.exposures.get_domain_data() > value)
        if any(exceeds):
            index = exceeds[0][0]
            rv.add_domain(self.domain.time[index])

        return rv


class Exceedance:

    def __init__(self):
        self.points = dict() 
        self.lines = dict()
        self.planes = dict()
        self.domain = None

    @property
    def any(self):
        if self.points or self.lines or self.planes or self.domain:
            return True
        else:
            return False
    
    def add_point(self, point_name: str, time: float):
        self.points[point_name] = time

    def add_line(self, line_name: str, time: float):
        self.lines[line_name] = time
    
    def add_plane(self, plane_name: str, time: float):
        self.planes[plane_name] = time
    
    def add_domain(self, time: float):
        self.domain = time

    def min_point(self):
        min_value = sys.float_info.max
        min_name = ""
        for name, time in self.points.items():
            if time < min_value:
                min_value = time
                min_name = name
        return min_name, min_value

    def min_line(self):
        min_value = sys.float_info.max
        min_name = ""
        for name, time in self.lines.items():
            if time < min_value:
                min_value = time
                min_name = name
        return min_name, min_value
    
    def min_plane(self):
        min_value = sys.float_info.max
        min_name = ""
        for name, time in self.planes.items():
            if time < min_value:
                min_value = time
                min_name = name
        return min_name, min_value

    def min(self):
        min_value = sys.float_info.max
        min_name = ""
        name, time = self.min_point()
        if time < min_value:
            min_value = time
            min_name = name
        name, time = self.min_line()
        if time < min_value:
            min_value = time
            min_name = name
        name, time = self.min_plane()
        if time < min_value:
            min_value = time
            min_name = name
        if self.domain:
            if self.domain < min_value:
                min_value = self.domain
                min_name = "domain"

        return min_name, min_value
