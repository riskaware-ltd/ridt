from base.settings import Settings
from base.settings import Terminus
from base.exceptions import ListTypeError
from base.exceptions import FloatTypeError
from base.exceptions import DimensionError


class IDMFConfig(Settings):

    @Settings.assign
    def __int__(self, values: dict):
        self.dispersion_model = str
        self.source_terms = SourceTerms
        self.inputs = Inputs


class SourceTerms(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.number_of_sources = int
        self.release_type = str


class Inputs(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.room_total_air_change_rate = float
        self.room_fresh_air_change_rate = float
        self.source_locations = CoordinatesList
        self.instantaneous = Instantaneous
        self.infinite_duration = InfiniteDuration
        self.fixed_duration = FixedDuration
        self.duration_of_analysis_period = float
        self.location_of_monitor_points = CoordinatesList
        self.contour_plots = ContourPlots
        self.output_units = OutputUnits
        self.thresholds = Thresholds
        self.eddy_diffusion = EddyDiffusion


class Instantaneous(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.release_mass = float
        self.release_time = float


class InfiniteDuration(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.release_rate = float
        self.release_time = float


class FixedDuration(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.release_mass = float
        self.release_time = float
        self.end_time = float


class ContourPlots(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.contour = bool
        self.concentration = bool
        self.exposure = bool
        self.planes = Planes
        self.frequency_of_contour_creation = float
        self.contour_range = str


class Planes(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.vertical = Vertical
        self.horizontal = Horizontal


class Vertical(Settings):

    @Settings.assign
    def __init__(self, values: dict):
        self.enable = bool
        self.number_of_planes = int
        self.point_planes_passes_through = CoordinatesList


class Horizontal(Settings):

    @Settings.assign
    def __int__(self, values: dict):
        self.enable = bool
        self.number_of_planes = int
        self.point_planes_passes_through = CoordinatesList


class OutputUnits(Settings):

    @Settings.assign
    def __int__(self, values: dict):
        self.concentration = str
        self.exposure = str


class Thresholds(Settings):

    @Settings.assign
    def __int__(self, values: dict):
        self.concentration = ThresholdList
        self.exposure = ThresholdList


class EddyDiffusion(Settings):

    @Settings.assign
    def __int__(self, values: dict):
        self.image_sources = ImageSources
        self.diffusion_coefficient_calculations = str
        self.diffusion_coefficient_value = float
        self.tkeb = TKEB


class ImageSources(Settings):

    @Settings.assign
    def __int__(self, values: dict):
        self.number_of_image_sources = int
        self.max_error_at_monitor_locations = float


class TKEB(Settings):

    @Settings.assign
    def __int__(self, values: dict):
        self.total_supply_flow_rate = float
        self.number_of_supply_vents = int


class ThresholdList(Terminus):

    @Terminus.assign
    def __int__(self, value: list):
        self.value = value

    def check(self):

        if not isinstance(self.value, list):
            raise ListTypeError(value)

        for entry in self.value:
            if not isinstance(entry, float) and not isinstance(entry, int):
                raise FloatTypeError(entry)


class CoordinatesList(Terminus):

    @Terminus.assign
    def __init__(self, value: list):
        self.value = value

    def check(self):

        if not isinstance(self.value, list):
            raise ListTypeError(self.value)

        for value in self.value:
            if not isinstance(value, list):
                raise ListTypeError(value)
            if len(value) != 3:
                raise DimensionError(value, 3)

            for entry in value:
                if not isinstance(entry, float) and not isinstance(entry, int):
                    raise FloatTypeError(entry)
