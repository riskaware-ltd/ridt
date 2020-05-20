import sys

from typing import List

from numpy import ndarray
from numpy import any
from numpy import where
from numpy import max
from numpy import argmax
from numpy import unravel_index
from numpy import std
from numpy import mean

from config import IDMFConfig

from container import Domain

from data import DataStore

from .exposure import Exposure
from .results import ThresholdResults
from .results import MaximumResults 



class DataStoreAnalyser:

    def __init__(self, setting: IDMFConfig, data_store: DataStore):
        self.setting = setting

        self.conc_data = data_store
        self.expo_data = Exposure(self.setting, data_store)

        self.domain = Domain(self.setting)

        self.conc_max = None
        self.expo_max = None

        self.conc_threshold_results = ThresholdResults(
            len(self.setting.thresholds.concentration))
        self.expo_threshold_results = ThresholdResults(
            len(self.setting.thresholds.exposure))
        
        self.conc_maximum_results = MaximumResults()
        self.expo_maximum_results = MaximumResults()

        self.phases = ["points", "lines", "planes", "domain"]
        self.loc = self.setting.models.eddy_diffusion.monitor_locations
        self.flags = self.setting.models.eddy_diffusion.analysis

    def evaluate_maximums(self):
        for phase in self.phases:
            if getattr(self.flags.maximum_anywhere, f"all_{phase}"):
                tmp = getattr(self.conc_maximum_results, phase)
                tmp.anywhere = self.maximum_anywhere(
                    getattr(self.conc_data, phase))
                setattr(self.conc_maximum_results, phase, tmp)

    def maximum_anywhere(self, data: Union[Dict[str, ndarray], ndarray]):
        rv = dict()
        if isinstance(data, ndarray):
            idx = unravel_index(argmax(data), data.shape)
            rv[idx[1:]] = self.domain.time[idx[0]]
            return rv
        else:
            max_val = 0.0
            max_name = ""
            for name, value in data.items():
                idx = unravel_index(argmax(value), value.shape)
                if value[*idx] > max_val:
                    max_val = value[*idx]
                    max_name = name
                    max_time = self.domain.time[idx[0]]
            rv[max_name] = max_time
            return rv
        
    def evaluate_thresholds(self):
        phases = ["points", "lines", "planes", "domain"]
        percent_threshold = self.setting\
                                .models\
                                .eddy_diffusion\
                                .analysis\
                                .threshold_percentage\
                                .percentage

        percent_maximum = self.setting\
                              .models\
                              .eddy_diffusion\
                              .analysis\
                              .maximum_percentage\
                              .percentage

        for idx, conc in enumerate(self.setting.thresholds.concentration):
            for phase in self.phases:
                tmp = getattr(self.conc_threshold_results, phase)
                if getattr(self.flags.threshold_percentage, f"all_{phase}"):
                    tmp[idx].percentage = self.threshold_percentage(
                        getattr(self.conc_data, phase), conc, percent_threshold)
                if getattr(self.flags.maximum_percentage, f"all_{phase}"):
                    tmp[idx].maximum = self.maximum_percentage(
                        getattr(self.conc_data, phase), conc, percent_maximum)
                if getattr(self.flags.threshold_anywhere, f"all_{phase}"):
                    tmp[idx].anywhere = self.threshold_anywhere(
                        getattr(self.conc_data, phase), conc)
                setattr(self.conc_threshold_results, phase, tmp)
        for idx, expo in enumerate(self.setting.thresholds.expoentration):
            for phase in self.phases:
                tmp = getattr(self.expo_threshold_results, phase)
                if getattr(self.flags.threshold_percentage, f"all_{phase}"):
                    tmp[idx].percentage = self.threshold_percentage(
                        getattr(self.expo_data, phase), expo, percent_threshold)
                if getattr(self.flags.maximum_percentage, f"all_{phase}"):
                    tmp[idx].maximum = self.maximum_percentage(
                        getattr(self.expo_data, phase), conc, percent_maximum)
                if getattr(self.flags.threshold_anywhere, f"all_{phase}"):
                    tmp[idx].anywhere = self.threshold_anywhere(
                        getattr(self.expo_data, phase), expo)
                setattr(self.expo_threshold_results, phase, tmp)

    def threshold_percentage(self,
                             data: Union[Dict[str, ndarray], ndarray],
                             threshold: float,
                             percentage: float):
        if isinstance(data, ndarray):
            for i in range(self.setting.time_samples):
                d = self.setting.models.eddy_diffusion.spatial_samples
                s = d.x * d.y * d.z
                v = len(where(data[i, :, :, :] >= threshold)[0]) / s
                if v >= percentage:
                    return self.domain.time[i]
        else:
            for i in range(self.setting.time_samples):
                a = [max(item[i]) for item in data.values()]
                v = len([item for item in a if item >= threshold]) / len(a)
                if v >= percentage:
                    return self.domain.time[i]
        return None

    def threshold_anywhere(self,
                           data: Union[Dict[str, ndarray], ndarray],
                           threshold: float):
        rv = dict()
        if isinstance(data, ndarray):
            exceeds = where(data >= threshold)
            if any(exceeds):
                rv["domain"] = self.domain.time[exceeds[0][0]]
            return rv
        else:
            for name, data in data.items():
                exceeds = where(data >= threshold)
                if any(exceeds):
                    rv[name] = self.domain.time[exceeds[0][0]]
            return rv

    def maximum_percentage(self,
                           data: Union[Dict[str, ndarray], ndarray],
                           threshold: float,
                           percentage: float):
        max_value = 0.0
        if isinstance(data, ndarray):
            for i in range(self.setting.time_samples):
                d = self.setting.models.eddy_diffusion.spatial_samples
                s = d.x * d.y * d.z
                v = len(where(data[i, :, :, :] >= threshold)[0]) / s
                if v >= max_value:
                    max_value = v
        else:
            for i in range(self.setting.time_samples):
                a = [max(item[i]) for item in data.values()]
                v = len([item for item in a if item >= threshold]) / len(a)
                if v >= max_value:
                    max_value = v
        return max_value

    def time_to_well_mixed(self):
        for i in range(self.setting.time_samples):
            d = self.conc_data.domain[i, :, :, :]
            value = std(d) / mean(d)
            if value <= 0.1:
                return self.domain.time[i]
        return None

    def steady_state_well_mixed_concentration(self):
        pass

    def characteristic_diffusion_time(self):
        pass

    def max_exposure(self):
        value = 0.0
        name = ""


        for line_name, line in self.loc.lines.items():
            tmp = max(self.exposures.get_line_data(line_name))
            if tmp > value:
                value = tmp
                name = line_name

        for plane_name, plane in self.loc.planes.items():
            tmp = max(self.exposures.get_plane_data(plane_name))
            if tmp > value:
                value = tmp
                name = plane_name
        
        tmp = max(self.exposures.get_domain_data())
        if tmp > value:
            value = tmp
            name = "domain" 

        return name, value
        
    def time_to_percent_exposure(self, percent: float, exposure: float):
        if percent < 0 or percent > 1:
            raise ValueError("percent must be between zero and one.")
        data = self.exposures.get_domain_data()
        dimensions = self.setting.models.eddy_diffusion.dimensions
        size = dimensions.x * dimensions.y * dimensions.z
        for i in range(self.setting.time_samples):
            if len(where(data[i, :, :, :] > exposure)[0]) / size >= percent:
                return self.domain.time[i]
        return None

    def percent_exceed_exposure_lifetime(self, exposure):

        data = self.exposures.get_domain_data()
        dimensions = self.setting.models.eddy_diffusion.spatial_samples
        size = dimensions.x * dimensions.y * dimensions.z
        return len(where(data[-1, :, :, :] > exposure)[0]) / size

    def exceeds_exposure(self, value: float):
        rv = Exceedance()

        for point_name, point in self.loc.points.items():
            exceeds = where(self.exposures.get_point_data(point_name) > value)
            if any(exceeds):
                index = exceeds[0][0]
                rv.add_point(point_name, self.domain.time[index])

        for line_name, line in self.loc.lines.items():
            exceeds = where(self.exposures.get_line_data(line_name) > value)
            if any(exceeds):
                index = exceeds[0][0]
                rv.add_line(line_name, self.domain.time[index])

        for plane_name, plane in self.loc.planes.items():
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
        self.loc.points = dict() 
        self.loc.lines = dict()
        self.loc.planes = dict()
        self.domain = None

    @property
    def any(self):
        if self.loc.points or self.loc.lines or self.loc.planes or self.domain:
            return True
        else:
            return False
    
    def add_point(self, point_name: str, time: float):
        self.loc.points[point_name] = time

    def add_line(self, line_name: str, time: float):
        self.loc.lines[line_name] = time
    
    def add_plane(self, plane_name: str, time: float):
        self.loc.planes[plane_name] = time
    
    def add_domain(self, time: float):
        self.domain = time

    def min_point(self):
        min_value = sys.float_info.max
        min_name = ""
        for name, time in self.loc.points.items():
            if time < min_value:
                min_value = time
                min_name = name
        return min_name, min_value

    def min_line(self):
        min_value = sys.float_info.max
        min_name = ""
        for name, time in self.loc.lines.items():
            if time < min_value:
                min_value = time
                min_name = name
        return min_name, min_value
    
    def min_plane(self):
        min_value = sys.float_info.max
        min_name = ""
        for name, time in self.loc.planes.items():
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
