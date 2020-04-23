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
        self.total_time = Time
        self.time_step = NonNegativeFloat
        self.total_air_change_rate = NonNegativeFloat
        self.fresh_air_change_rate = NonNegativeFloat

        self.instantaneous = InstantaneousSettings
        self.infinite_duration = InfiniteDurationSettings
        self.fixed_duration = FixedDurationSettings
        self.monitor_locations = MonitorLocations
        self.thresholds = Thresholds
        self.output_units = OutputUnits

        self.eddy_diffusion = EddyDiffusion
        self.well_mixed = WellMixed

    def consistency_check(self):
        if self.total_time < self.time_interval:
            raise ValueError("Time interval must be less than the total time.")
        if self.eddy_diffusion.dimensions.x < self.eddy_diffusion.dimensions.spatial_step:
            raise ValueError("The spatial step cannot be less than the x dimension.")


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


class OutputUnits(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.concentration = str
        self.exposure = str


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
        self.spatial_units = str
        self.x = CoordinateValue
        self.y = CoordinateValue
        self.z = CoordinateValue
        self.spatial_step = NonNegativeFloat


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
        self.contour_range = str
        self.manual_contours = ManualContours


class Planes(Dict):

    @Dict.assign
    def __init__(self, values: dict):
        self.value = Plane


class Plane(Settings):

    @Settings.assign
    def __init__(self, value: dict):
        self.axis = str
        self.distance = NonNegativeFloat


class ManualContours(List):

    @List.assign
    def __init__(self, value: dict):
        self.value = NonNegativeFloat


class WellMixed(Settings):

    @Settings.assign
    def __init__(self, value: dict):
        self.volume = Volume


class CoordinateValue(Terminus):

    @Terminus.assign
    def __init__(self, value: dict):
        self.value = value

    def check(self):
        if not isinstance(self.value, float):
            raise TypeError("Coordinate value must be a float.")
        if self.value < 0:
            raise ValueError("Coordinate value must be non negative.")


class Mass(Terminus):

    @Terminus.assign
    def __init__(self, value: dict):
        self.value = value

    def check(self):
        if not isinstance(self.value, float):
            raise TypeError("Mass must be a float")
        if self.value < 0:
            raise ValueError("Mass must be non negative")


class Time(Terminus):

    @Terminus.assign
    def __init__(self, value: dict):
        self.value = value

    def check(self):
        if not isinstance(self.value, float):
            raise TypeError("Mass must be a float")
        if self.value < 0:
            raise ValueError("Mass must be non negative")


class Percentage(Terminus):

    @Terminus.assign
    def __init__(self, value: dict):
        self.value = value

    def check(self):
        if not isinstance(self.value, float):
            raise TypeError("Percentage value must be a float")
        if self.value < 0:
            raise ValueError("Percentage value must not be non zero")


class Volume(Terminus):

    @Terminus.assign
    def __init__(self, value: dict):
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
    def __init__(self, value):
        self.value = value

    def check(self):
        if not isinstance(self.value, float):
            raise ValueError("Value must be a float")
        if self.value < 0:
            raise ValueError("Value must be non negative.")
