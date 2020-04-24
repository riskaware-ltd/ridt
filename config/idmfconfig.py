from base.settings import Settings
from base.settings import Terminus
from base.settings import List
from base.settings import Dict


class IDMFConfig(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.dispersion_model = str
        self.release_type = str

        self.time_units = str
        self.time_discretisation = int
        self.total_time = Time
        self.concentration_units = str
        self.exposure_units = str

        self.spatial_units = str
        self.spatial_discretisation = int
        self.total_air_change_rate = NonNegativeFloat
        self.fresh_air_change_rate = NonNegativeFloat

        self.instantaneous = InstantaneousSettings
        self.infinite_duration = InfiniteDurationSettings
        self.fixed_duration = FixedDurationSettings
        self.monitor_locations = MonitorLocations
        self.thresholds = Thresholds

        self.eddy_diffusion = EddyDiffusion
        self.well_mixed = WellMixed

    def consistency_check(self):
        for key, value in self.fixed_duration.sources.value.items():
            if value.end_time < value.start_time:
                raise ValueError("The start time must be smaller than the end time.")
        if len([val for val in self.thresholds.concentration.value]) > 5:
            raise ValueError("Maximum of five concentration thresholds allowed")
        if len([val for val in self.thresholds.exposure.value]) > 5:
            raise ValueError("Maximum of five concentration thresholds allowed")
        for key, val in self.eddy_diffusion.contour_plots.planes.value.items():
            if val.axis not in ["xy", "xz", "zy"]:
                raise ValueError(f"Plane {key} must be a xy, xz or zy plane.")
            if val.axis == "xy" and val.distance > self.eddy_diffusion.dimensions.z:
                raise ValueError(f"Plane {key} lies out of the container's border.")
            if val.axis == "xz" and val.distance > self.eddy_diffusion.dimensions.y:
                raise ValueError(f"Plane {key} lies out of the container's border.")
            if val.axis == "zy" and val.distance > self.eddy_diffusion.dimensions.x:
                raise ValueError(f"Plane {key} lies out of the container's border.")
        if self.eddy_diffusion.contour_plots.contours.min > self.eddy_diffusion.contour_plots.contours.max:
            raise ValueError("Manual contour min cannot be greater than manual contour max.")
        if self.eddy_diffusion.contour_plots.range not in ["auto", "manual"]:
            raise ValueError("Contour range must be either auto or manual.")
        if self.eddy_diffusion.contour_plots.scale not in ["linear", "logarithmic"]:
            raise ValueError("Contour scale must be either linear or logarithmic.")
        if self.release_type not in ["instantaneous", "infiniteduration", "fixedduration"]:
            raise ValueError("Release type must be either "
                             "instantaneous, infiniteduration or fixedduration.")
        if self.dispersion_model not in ["well_mixed", "eddy_diffusion"]:
            raise ValueError("Dispersion model muse be either well_mixed or eddy_diffusion.")
        if self.time_units not in ["s", "m", "h"]:
            raise ValueError("Time units must be either s, m or h.")
        if self.concentration_units not in ["kgm-3", "mgm-3", "kgm-3", "ppm", "ppb", "ppt"]:
            raise ValueError("Concentration units must be kgm-3, mgm-3, kgm-3, ppm, ppb or ppt.")
        if self.exposure_units not in ["mgminm-3", "kgsm-3"]:
            raise ValueError("Exposure units must be mgminm-3 or kgsm-3.")
        if self.spatial_units not in ["mm", "cm", "m"]:
            raise ValueError("Spatial units must be mm, cm or m.")


class InstantaneousSettings(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.sources = InstantaneousSourceDict


class InstantaneousSourceDict(Dict):

    @Dict.assign
    def __init__(self, values: dict):
        self.value = InstantaneousSource


class InstantaneousSource(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.x = CoordinateValue
        self.y = CoordinateValue
        self.z = CoordinateValue
        self.mass = Mass
        self.time = Time


class InfiniteDurationSettings(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.sources = InfiniteDurationSourceDict


class InfiniteDurationSourceDict(Dict):

    @Dict.assign
    def __init__(self, values: dict):
        self.value = InfiniteDurationSource


class InfiniteDurationSource(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.x = CoordinateValue
        self.y = CoordinateValue
        self.z = CoordinateValue
        self.rate = NonNegativeFloat
        self.time = Time


class FixedDurationSettings(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.sources = FixedDurationSourceDict


class FixedDurationSourceDict(Dict):

    @Dict.assign
    def __init__(self, values: dict):
        self.value = FixedDurationSource


class FixedDurationSource(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.x = CoordinateValue
        self.y = CoordinateValue
        self.z = CoordinateValue
        self.rate = NonNegativeFloat
        self.start_time = Time
        self.end_time = Time


class MonitorLocations(Dict):

    @Dict.assign
    def __init__(self, values: dict):
        self.value = Monitor


class Monitor(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.x = CoordinateValue
        self.y = CoordinateValue
        self.z = CoordinateValue


class Thresholds(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.concentration = ThresholdList
        self.exposure = ThresholdList


class ThresholdList(List):

    @List.assign
    def __init__(self, values: list):
        self.value = Threshold


class EddyDiffusion(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.dimensions = Dimensions
        self.coefficient = Coefficient
        self.images = Images
        self.contour_plots = ContourPlots


class Dimensions(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.x = CoordinateValue
        self.y = CoordinateValue
        self.z = CoordinateValue


class Coefficient(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.calculation = str
        self.value = float
        self.tkeb = TKEB


class TKEB(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.number_of_supply_vents = int


class Images(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.quantity = int
        self.max_error = Percentage


class ContourPlots(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.contour = bool
        self.concentration = bool
        self.exposure = bool
        self.planes = Planes
        self.creation_frequency = NonNegativeFloat
        self.number_of_contours = int
        self.range = str
        self.scale = str
        self.contours = ManualContours


class Planes(Dict):

    @Dict.assign
    def __init__(self, values: dict):
        self.value = Plane


class Plane(Settings):

    @Settings.assign
    def __init__(self, value: dict):
        self.axis = str
        self.distance = NonNegativeFloat


class ManualContours(Settings):

    @Settings.assign
    def __init__(self, value: dict):
        self.min = NonNegativeFloat
        self.max = NonNegativeFloat


class WellMixed(Settings):

    @Settings.assign
    def __init__(self, value: dict):
        self.volume = Volume


class CoordinateValue(Terminus):

    @Terminus.assign
    def __init__(self, value: float):
        self.value = float

    def check(self):
        if not isinstance(self.value, float):
            raise TypeError("Coordinate value must be a float.")
        if self.value < 0:
            raise ValueError("Coordinate value must be non negative.")


class Mass(Terminus):

    @Terminus.assign
    def __init__(self, value: float):
        self.value = float

    def check(self):
        if not isinstance(self.value, float):
            raise TypeError("Mass must be a float")
        if self.value < 0:
            raise ValueError("Mass must be non negative")


class Time(Terminus):

    @Terminus.assign
    def __init__(self, value: float):
        self.value = float

    def check(self):
        if not isinstance(self.value, float):
            raise TypeError("Mass must be a float")
        if self.value < 0:
            raise ValueError("Mass must be non negative")


class Percentage(Terminus):

    @Terminus.assign
    def __init__(self, value: float):
        self.value = float

    def check(self):
        if not isinstance(self.value, float):
            raise TypeError("Percentage value must be a float")
        if self.value < 0:
            raise ValueError("Percentage value must not be non zero")


class Volume(Terminus):

    @Terminus.assign
    def __init__(self, value: float):
        self.value = float

    def check(self):
        if not isinstance(self.value, float):
            raise TypeError("Volume must be a float")
        if self.value < 0:
            raise ValueError("Volume must not be non zero")


class Threshold(Terminus):

    @Terminus.assign
    def __init__(self, value: float):
        self.value = float

    def check(self):
        if not isinstance(self.value, float):
            raise ValueError("Threshold value must be a float")
        if self.value < 0:
            raise ValueError("Coordinate value must be non negative.")


class NonNegativeFloat(Terminus):

    @Terminus.assign
    def __init__(self, value: float):
        self.value = float

    def check(self):
        if not isinstance(self.value, float):
            raise ValueError("Value must be a float")
        if self.value < 0:
            raise ValueError("Value must be non negative.")
