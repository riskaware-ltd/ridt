from base.settings import Settings
from base.settings import Terminus
from base.settings import List
from base.settings import Dict
from base.settings import Number


class IDMFConfig(Settings):

    """The :class:`~.IDMFConfig` class. It inherits from
    :class:`~.Settings`. For information about the behaviour of
    :class:`~..Settings` derived classes, please refer to the :class:`~..Settings`
    documentation.

    Attributes
    ---------
    dispersion_model: :obj:`str`
        A string selecting the type of dispersion model.

    release_type: :obj:`str`
        A string selecting the release type.

    time_units: :obj:`str`
        A string dictating the units of time used within the
        simulation.

    time_samples: :obj:`int`
        The number of intervals that the total time is split
        up into.

    total_time: :class:`~.NonNegativeFloat`
        A non negative float which corresponds to the total
        time of the simulation.

    concentration_units: :obj:`str`
        The units of the concentration of the material.

    exposure_units: :obj:`str`
        The units of the exposure of the material
        within the container.

    spatial_units: :obj:`str`
        The spatial units of the container.

    spatial_samples: :obj:`int`
        The number of intervals that the container is split
        up into.

    total_air_change_rate: :class:`~.NonNegativeFloat`
        The total air change rate in the system.

    fresh_air_change_rate: :class:`~.NonNegativeFloat`
        The fresh air change rate in the system.

    monitor_locations: :class:`~.MonitorLocations`
        A :class:`~.Dict` child that contains paths
        to the MonitorLocations configurations.

    thresholds: :class:`~.NonNegativeFloats`
        A :class:`~.Settings` child containing the paths to the Threshold
        configurations.
    
    modes : :class:`~.ModeSettings`
        A :class:`~.Settings` child containin mode specific settings.

    models : :class:`~.ModelSettings`
        A :class:`~.Settings` child containin model specific settings.

    Returns
    -------
    None

    """
    @Settings.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.IDMFConfig` class.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary corresponding to the read in .json
            config file.

        Returns
        -------
        None

        """
        self.dispersion_model = str
        self.release_type = str

        self.time_units = str
        self.time_samples = int
        self.total_time = NonNegativeFloat
        self.concentration_units = str
        self.exposure_units = str

        self.spatial_units = str
        self.spatial_samples = int
        self.total_air_change_rate = NonNegativeFloat
        self.fresh_air_change_rate = NonNegativeFloat

        self.modes = ModeSettings
        self.monitor_locations = MonitorLocations
        self.thresholds = Thresholds

        self.models = ModelSettings

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


class ModelSettings(Settings):
    """The :class:`~.ModelSettings` class. It inherits from :class:`~.Settings`
    class

    Attributes
    ----------
    eddy_diffusion: :class:`~.EddyDiffusion`
        A :class:`~.Settings` child containing the paths
        to the EddyDiffusion configurations.

    well_mixed: :class:`~.WellMixed`
        A :class:`~.Settings` child containing the paths
        to the WellMixed configurations.

    """
    @Settings.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.ModelSettings` class.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary corresponding to the instantaneous
            settings configurations.
        """
        self.eddy_diffusion = EddyDiffusion
        self.well_mixed = WellMixed


class ModeSettings(Settings):
    """The :class:`~.ModeSettings` class. It inherits from :class:`~.Settings`
    class

    Attributes
    ----------
    instantaneous: :class:`~.InstantaneousSettings`
        A :class:`~.Settings` child that contains paths
        to the Instantaneous configurations.

    infinite_duration: :class:`~.InfiniteDurationSettings`
        A :class:`~.Settings` child that contains paths
        to the InfiniteDuration configurations.

    fixed_duration: :class:`~.FixedDurationSettings`
        A :class:`~.Settings` child that contains paths
        to the FixedDuration configurations.

    """
    @Settings.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.InstantaneousSettings` class.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary corresponding to the instantaneous
            settings configurations.
        """
        self.instantaneous = InstantaneousSettings
        self.infinite_duration = InfiniteDurationSettings
        self.fixed_duration = FixedDurationSettings


class InstantaneousSettings(Settings):

    """The :class:`~.InstantaneousSettings` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    sources: :class:`~.Dict`
        Path to the dictionary of instantaneous sources within
        the simulation.
    """

    @Settings.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.InstantaneousSettings` class.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary corresponding to the instantaneous
            settings configurations.
        """

        self.sources = InstantaneousSourceDict


class InstantaneousSourceDict(Dict):

    @Dict.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.InstantaneousSourceDict` class.

        Parameters
        ----------
        values : :obj:`dict`
            The value corresponding to the instantaneous
            source configurations.
        """
        self.type = InstantaneousSource


class InstantaneousSource(Settings):
    """The :class:`~.InstantaneousSource` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    x: :class:`~.NonNegativeFloat`
        The x coordinate of the source.
    y: :class:`~.NonNegativeFloat`
        The y coordinate of the source.
    z: :class:`~.NonNegativeFloat`
        The z coordinate of the source.
    mass: :class:`~.NonNegativeFloat`
        The mass of the material released.
    time: :class:`~.NonNegativeFloat`
        The time that the material is released.
    """
    @Settings.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.InstantaneousSource` class.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary corresponding to the instantaneous
            sources.
        """
        self.x = NonNegativeFloat
        self.y = NonNegativeFloat
        self.z = NonNegativeFloat
        self.mass = NonNegativeFloat
        self.time = NonNegativeFloat


class InfiniteDurationSettings(Settings):
    """The :class:`~.InfiniteDurationSettings` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    sources: :class:`~.Dict`
        Path to the dictionary of infinite duration sources within
        the simulation.
    """
    @Settings.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.InfiniteDurationSettings` class.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary corresponding to the infinite duration
            sources.
        """
        self.sources = InfiniteDurationSourceDict


class InfiniteDurationSourceDict(Dict):

    @Dict.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.InfiniteDurationSourceDict` class.

        Parameters
        ----------
        values : :obj:`dict`
            The value corresponding to the infinite duration
            sources.
        """
        self.type = InfiniteDurationSource


class InfiniteDurationSource(Settings):
    """The :class:`~.InfiniteDurationSource` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    x: :class:`~.NonNegativeFloat`
        The x coordinate of the source.
    y: :class:`~.NonNegativeFloat`
        The y coordinate of the source.
    z: :class:`~.NonNegativeFloat`
        The z coordinate of the source.
    rate: :class:`~.NonNegativeFloat`
        The mass of the material released.
    time: :class:`~.NonNegativeFloat`
        The time that the material is released.
    """
    @Settings.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.InfiniteDurationSource` class.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary corresponding to the infinite duration
            sources configurations.
        """
        self.x = NonNegativeFloat
        self.y = NonNegativeFloat
        self.z = NonNegativeFloat
        self.rate = NonNegativeFloat
        self.time = NonNegativeFloat


class FixedDurationSettings(Settings):
    """The :class:`~.FixedDurationSettings` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    sources: :class:`~.Dict`
        Path to the dictionary of fixed duration sources within
        the simulation.
    """
    @Settings.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.FixedDurationSettings` class.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary corresponding to the fixed duration sources.
        """
        self.sources = FixedDurationSourceDict


class FixedDurationSourceDict(Dict):

    @Dict.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.FixedDurationSourceDict` class.

        Parameters
        ----------
        values : :obj:`dict`
            The value corresponding to the fixed duration sources.
        """
        self.type = FixedDurationSource


class FixedDurationSource(Settings):
    """The :class:`~.FixedDurationSource` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    x: :class:`~.NonNegativeFloat`
        The x coordinate of the source.
    y: :class:`~.NonNegativeFloat`
        The y coordinate of the source.
    z: :class:`~.NonNegativeFloat`
        The z coordinate of the source.
    rate: :class:`~.NonNegativeFloat`
        The mass of the material released.
    start_time: :class:`~.NonNegativeFloat`
        The time that the material is released.
    end_time: :class:`~.NonNegativeFloat`
        The time that the source stops emitting
        the material.
    """
    @Settings.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.FixedDurationSource` class.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary corresponding to the fixed duration
             sources configurations.
        """
        self.x = NonNegativeFloat
        self.y = NonNegativeFloat
        self.z = NonNegativeFloat
        self.rate = NonNegativeFloat
        self.start_time = NonNegativeFloat
        self.end_time = NonNegativeFloat


class MonitorLocations(Dict):

    @Dict.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.MonitorLocations` class.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary corresponding to the fixed duration
             sources configurations.
        """
        self.type = Monitor


class Monitor(Settings):
    """The :class:`~.Monitor` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    x: :class:`~.NonNegativeFloat`
        The x coordinate of the monitor.
    y: :class:`~.NonNegativeFloat`
        The y coordinate of the monitor.
    z: :class:`~.NonNegativeFloat`
        The z coordinate of the monitor.
    """
    @Settings.assign
    def __init__(self, values: dict):
        self.x = NonNegativeFloat
        self.y = NonNegativeFloat
        self.z = NonNegativeFloat


class Thresholds(Settings):
    """The :class:`~.Thresholds` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    concentration: :class:`~.ThresholdList`
        Path to the list of concentration thresholds within
        the simulation.
    exposure: :class:`~.ThresholdList`
        Path to the list of exposure thresholds within
        the simulation.
    """
    @Settings.assign
    def __init__(self, values: dict):
        self.concentration = ThresholdList
        self.exposure = ThresholdList


class ThresholdList(List):

    @List.assign
    def __init__(self, values: list):
        self.type = NonNegativeFloat


class EddyDiffusion(Settings):
    """The :class:`~.EddyDiffusion` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    dimensions: :class:`~.Dimensions`
        Path to the dimensions of the container.
    coefficient: :class:`~.Coefficient`
        Path to the eddy diffusion
        coefficient calculations.
    images: :class:`~.Images`
        Path to the image configurations.
    contour_plots: :class:`~.ContourPlots`
        Path to the contour plots configurations.
    """
    @Settings.assign
    def __init__(self, values: dict):
        self.dimensions = Dimensions
        self.coefficient = Coefficient
        self.images = Images
        self.contour_plots = ContourPlots


class Dimensions(Settings):
    """The :class:`~.Dimensions` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    x: :class:`~.NonNegativeFloat`
        The x magnitude of the container.
    y: :class:`~.NonNegativeFloat`
        The y magnitude of the container.
    z: :class:`~.NonNegativeFloat`
        The z magnitude of the container.
    """
    @Settings.assign
    def __init__(self, values: dict):
        self.x = NonNegativeFloat
        self.y = NonNegativeFloat
        self.z = NonNegativeFloat


class Coefficient(Settings):
    """The :class:`~.Coefficient` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    calculation: :obj:`str`
        A string dictating the way the eddy diffusion
        coefficient will be calculated.
    value: :obj:`float`
        The explicit value of the eddy diffusion coefficient.
    tkeb: :class:`~.TKEB`
        The path leading to the TKEB configurations.
    """
    @Settings.assign
    def __init__(self, values: dict):
        self.calculation = str
        self.value = float
        self.tkeb = TKEB


class TKEB(Settings):
    """The :class:`~.TKEB` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    number_of_supply_vents: :obj:`int`
        The number of supply vents in the system.
    """
    @Settings.assign
    def __init__(self, values: dict):
        self.number_of_supply_vents = int


class Images(Settings):
    """The :class:`~.Images` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    quantity: :obj:`int`
        The number of images.
    max_error: :class:`~.Percentage`
        The max error allowed when changing the number of image sources by 1.
    """
    @Settings.assign
    def __init__(self, values: dict):
        self.quantity = int
        self.max_error = Percentage


class ContourPlots(Settings):
    """The :class:`~.ContourPlots` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    contour: :obj:`bool`
        Whether or not we have contour plots.
    concentration: :obj:`bool`
        Show contour plots of the concentration value.
    exposure: :obj:`bool`
        Show the contour plots of the exposure value.
    planes: :class:`~.Planes`
        The planes where the contour plots are located.
    creation_frequency: :class:`~.NonNegativeFloat`
        How often we wish to create a contour plot of each plane in 1/s.
    number_of_contours: :obj:`int`
        The number of contours depicted.
    range: :obj:`str`
        The range of the contours. Can be auto
        or manually set.
    scale: :obj:`str`
        The scale of the contours. Either logarithmic
        or linear.
    contours: :class:`~.ManualContours`
        If range is manual. Then set the min and max
        values of the contours.
    """
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
        self.type = Plane


class Plane(Settings):
    """The :class:`~.Plane` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    axis: :obj:`str`
        Either an xy, zy, or xz plane.
    distance: :class:`~.NonNegativeFloat`
        How far along the remaining axis
        this plane is.
    """
    @Settings.assign
    def __init__(self, value: dict):
        self.axis = str
        self.distance = NonNegativeFloat


class ManualContours(Settings):
    """The :class:`~.ManualContours` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    min: :class:`~.NonNegativeFloat`
        The min value of the contours.
    max: :class:`~.NonNegativeFloat`
        The max value of the contours.

    """
    @Settings.assign
    def __init__(self, value: dict):
        self.min = NonNegativeFloat
        self.max = NonNegativeFloat


class WellMixed(Settings):
    """The :class:`~.WellMixed` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    volume: :class:`~.NonNegativeFloat`
        The total volume of the container.
    """
    @Settings.assign
    def __init__(self, value: dict):
        self.volume = NonNegativeFloat


class Percentage(Number):

    @Terminus.assign
    def __init__(self, value: float):
        self.type = float

    def check(self):
        self.lower_bound(0.0)
        self.upper_bound(100.0)


class NonNegativeFloat(Number):

    @Terminus.assign
    def __init__(self, value: float):
        self.type = float

    def check(self):
        self.lower_bound(0.0)
