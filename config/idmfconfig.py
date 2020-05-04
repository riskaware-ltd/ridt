from base.settings import Settings
from base.settings import Terminus
from base.settings import List
from base.settings import Dict
from base.settings import Number
from base.settings import StringSelection
from base.exceptions import Error


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

    time_units: :class:`~.TimeUnits` 
        A string dictating the units of time used within the
        simulation.

    time_samples: :obj:`int`
        The number of intervals that the total time is split
        up into.

    total_time: :class:`~.NonNegativeFloat`
        A non negative float which corresponds to the total
        time of the simulation.

    concentration_units: :class:`~.ConcentrationUnits` 
        The units of the concentration of the material.

    exposure_units: :class:`~.ExposureUnits` 
        The units of the exposure of the material
        within the container.

    spatial_units: :class:`~.SpatialUnits` 
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
        self.dispersion_model = DispersionModel
        self.release_type = ReleaseType

        self.time_units = TimeUnits
        self.time_samples = NonNegativeInteger
        self.total_time = NonNegativeFloat

        self.concentration_units = ConcentrationUnits
        self.exposure_units = ExposureUnits

        self.total_air_change_rate = NonNegativeFloat
        self.fresh_air_change_rate = NonNegativeFloat

        self.modes = ModeSettings
        self.thresholds = Thresholds

        self.models = ModelSettings

    def consistency_check(self):
        """Checker to be called after instantiating the :class:`~.IDMFConfig` class.
        Maintains that certain requirements are met and caught before initializing the run.
        Raises
        ------
        ValueError
            If the end time of a fixed duration source is less than the start time.

        ValueError
            If there are more than five concentration or exposure thresholds.

        ValueError
            If the type of plane does not coincide with an orthogonal axis.

        ValueError
            If the plane lies outside of the dimensions of the container.

        ValueError
            If the min value of the manual contour is greater than the max value.

        ValueError
            If the contour range type is not manual or auto.

        ValueError
            If the contour scaling is not linear or logarithmic.

        ValueError
            if the release type is not instantaneous, fixedduration
            or infiniteduration.

        ValueError
            If the type of dispersion model is not well mixed or
            eddy diffusion.

        ValueError
            If the time units are not seconds, minutes or hours.

        ValueError
            If the concentration units are not
            kgm-3, mgm-3, kgm-3, ppm, ppb or ppt.

        ValueError
            If the exposure units are not
             mgminm-3 or kgsm-3.

        ValueError
            If the spatial units are not mm, cm, m.
        """

        for mode in ["instantaneous", "infinite_duration", "fixed_duration"]:
            for key, value in getattr(self.modes, mode).sources.items():
                dim = self.models.eddy_diffusion.dimensions
                for axis in ["x", "y", "z"]:
                    par = getattr(value, axis)
                    bound = getattr(dim, axis)
                    if isinstance(par, list):
                        for item in par:
                            if item < 0 or item > bound:
                                raise ConsistencyError(
                            f"{mode} source {key} x position is "
                            f"outside simulation space domain (0, {bound}).")
                    else:
                        if par < 0 or par > bound:
                            raise ConsistencyError(
                        f"{mode} source {key} x position is "
                        f"outside simulation space domain (0, {bound}).")


        for mode in ["instantaneous", "infinite_duration"]:
            for key, value in getattr(self.modes, mode).sources.items():
                if isinstance(value.time, list):
                    for item in value.time:
                        if item > self.total_time:
                            raise ConsistencyError(
                        f"{mode} source {key} time is "
                        f"outside simulation time domain [0, {self.total_time}).")
                else:
                    if value.time > self.total_time:
                        raise ConsistencyError(
                    f"{mode} source {key} time is "
                    f"outside simulation time domain [0, {self.total_time}).")

        for key, value in getattr(self.modes, "fixed_duration").sources.items():
            if isinstance(value.start_time, list):
                for item in value.start_time:
                    if item > self.total_time:
                        raise ConsistencyError(
                    f"{mode} source {key} start time is "
                    f"outside simulation time domain [0, {self.total_time}).")
            else:
                if value.start_time > self.total_time:
                    raise ConsistencyError(
                f"{mode} source {key} start time is "
                f"outside simulation time domain [0, {self.total_time}).")

            if isinstance(value.end_time, list):
                for item in value.end_time:
                    if item > self.total_time:
                        raise ConsistencyError(
                    f"{mode} source {key} end time is "
                    f"outside simulation time domain [0, {self.total_time}).")
            else:
                if value.end_time > self.total_time:
                    raise ConsistencyError(
                f"{mode} source {key} end time is "
                f"outside simulation time domain [0, {self.total_time}).")

        contours = self.models.eddy_diffusion.contour_plots.contours
        if contours.min >= contours.max:
            raise ConsistencyError(
        f"contour min ({contours.min}) >= contour max ({contours.max}).")


class DispersionModel(StringSelection):
    """The dispersion model selection setting class.

    It inherits from :class:`~.StringSelection`.

    """
    @Terminus.assign
    def __init__(self, value: str):
        """The constructor for the :class:`DispersionModel` class.

        value : :obj:`str`
            The string indicating the dispersion model selection.
        """
        self.options = [
            "eddy_diffusion",
            "well_mixed"
        ]

    def check(self):
        pass


class ReleaseType(StringSelection):
    """The release type selection setting class.

    It inherits from :class:`~.StringSelection`.

    """
    @Terminus.assign
    def __init__(self, valu: str):
        """The constructor for the :class:`ReleaseType` class.

        value : :obj:`str`
            The string indicating the release type selection.
        """
        self.options = [
            "instantaneous",
            "infinite_duration",
            "fixed_duration"
        ]

    def check(self):
        pass


class TimeUnits(StringSelection):
    """The time units selection setting class.

    It inherits from :class:`~.StringSelection`.

    """
    @Terminus.assign
    def __init__(self, valu: str):
        """The constructor for the :class:`TimeUnits` class.

        value : :obj:`str`
            The string indicating the time units selection.
        """
        self.options = [
            "s",
            "m",
            "h"
        ]

    def check(self):
        pass


class ConcentrationUnits(StringSelection):
    """The time units selection setting class.

    It inherits from :class:`~.StringSelection`.

    """
    @Terminus.assign
    def __init__(self, valu: str):
        """The constructor for the :class:`ConcentrationUnits` class.

        value : :obj:`str`
            The string indicating the concentration units selection.
        """
        self.options = [
            "kgm-3",
            "mgm-3",
            "kgm-3",
            "ppm",
            "ppb",
            "ppt"
        ]
    def check(self):
        pass


class ExposureUnits(StringSelection):
    """The time units selection setting class.

    It inherits from :class:`~.StringSelection`.

    """
    @Terminus.assign
    def __init__(self, valu: str):
        """The constructor for the :class:`ExposureUnits` class.

        value : :obj:`str`
            The string indicating the exposure units selection.
        """
        self.options = [
            "mgminm-3",
            "kgsm-3"
        ]

    def check(self):
        pass


class SpatialUnits(StringSelection):
    """The time units selection setting class.

    It inherits from :class:`~.StringSelection`.

    """
    @Terminus.assign
    def __init__(self, valu: str):
        """The constructor for the :class:`SpatialUnits` class.

        value : :obj:`str`
            The string indicating the spatial units selection.
        """
        self.options = [
            "m",
            "cm",
            "mm"
        ]

    def check(self):
        pass


class ConsistencyError(Error):
    """The exception raised if a consistency check is failed.

    """

    def __init__(self, msg: str):
        """The constructor for the :class:`ConsistencyError` class

        Parameters
        ----------

        """
        super().__init__(msg)


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
        """The constructor for the :class:`~.ModeSettings` class.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary corresponding to the mode settings
            configurations.
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
    """The :class:`~.InstantaneousSourceDict` class. It inherits from
    :class:`~.Dict`.

    Attributes
    ---------
    type: :class:`~.InstantaneousSource`
        Path to the dictionary of values of the instantaneous
        sources.
    """
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
    """The :class:`~.InfiniteDurationSourceDict` class. It inherits from
     :class:`~.Dict`.

     Attributes
     ---------
     type: :class:`~.InfiniteDurationSource`
         Path to the dictionary of values of the infinite duration
         sources.
     """
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

    """The :class:`~.FixedDurationSourceDict` class. It inherits from
    :class:`~.Dict`.

    Attributes
    ---------
    type: :class:`~.FixedDurationSource`
        Path to the dictionary of values of the fixed duration
        sources.
    """

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


class Point(Settings):
    """The :class:`~.Point` class. It inherits from :class:`~.Settings`.

    Attributes
    ---------
    x: :class:`~.NonNegativeFloat`
        The x coordinate of the point.
    y: :class:`~.NonNegativeFloat`
        The y coordinate of the point.
    z: :class:`~.NonNegativeFloat`
        The z coordinate of the point.
    """
    @Settings.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.Point` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the point location.
        """
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
        """The constructor for the :class:`~.Thresholds` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the exposure
            and concentration thresholds.
        """
        self.concentration = ThresholdList
        self.exposure = ThresholdList


class ThresholdList(List):
    """The :class:`~.ThresholdList` class. It inherits from
    :class:`~.List`.

    Attributes
    ---------
    type: :class:`~.Threshold`
        Path to the dictionary of values of the thresholds
        in the simulation.
    """
    @List.assign
    def __init__(self, values: list):
        """The constructor for the :class:`~.ThresholdList` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the thresholds.
        """
        self.type = NonNegativeFloat


class EddyDiffusion(Settings):
    """The :class:`~.EddyDiffusion` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    dimensions: :class:`~.Dimensions`
        Path to the dimensions of the container.

    spatial_samples: :class:`~.SpatialSamples`
        Path to the spatial_samples container.

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
        """The constructor for the :class:`~.EddyDiffusion` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the eddy diffusion
            model type.
        """
        self.spatial_units = SpatialUnits
        self.dimensions = Dimensions
        self.spatial_samples = SpatialSamples
        self.monitor_locations = MonitorLocations
        self.coefficient = Coefficient
        self.images = Images
        self.contour_plots = ContourPlots
        self.line_plots = LinePlots


class LinePlots(Settings):
    """The :class:`~.LinePlots` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ----------
    output : :obj:`bool`
        Whether or not we output the contour plots.

    """
    @Settings.assign
    def __init__(self, values: dict):
        self.output = bool


class MonitorLocations(Settings):
    """The :class:`~.MonitorLocations` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    points : :class:`~.Points`
        The dictionary of points to be monitored.

    lines : :class:`~.Lines`
        The dictionary of lines to be monitored.

    planes : :class:`~.Planes`
        The dictionary of planes to be monitored.

    """
    @Settings.assign
    def __init__(self, values: dict):
        self.points = Points
        self.lines = Lines
        self.planes = Planes

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
        """The constructor for the :class:`~.Dimensions` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the dimensions
            of the container.
        """
        self.x = NonNegativeFloat
        self.y = NonNegativeFloat
        self.z = NonNegativeFloat


class SpatialSamples(Settings):
    """The :class:`~.SpatialSamples` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    x: :class:`~.NonNegativeInteger`
        The x magnitude of the container.
    y: :class:`~.NonNegativeInteger`
        The y magnitude of the container.
    z: :class:`~.NonNegativeInteger`
        The z magnitude of the container.
    """
    @Settings.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.SpatialSamples` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the spatial samples
            of the container.
        """
        self.x = NonNegativeInteger
        self.y = NonNegativeInteger
        self.z = NonNegativeInteger


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
        """The constructor for the :class:`~.Coefficient` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the coefficient
            calculations.
        """
        self.calculation = CoefficientMode
        self.value = ExplicitCoefficient
        self.tkeb = TKEB


class CoefficientMode(StringSelection):
    """The diffusion coefficient mode selection
    It inherits from :class:`~.Terminus`.

    """
    @Terminus.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`CoefficientMode` class.

        value : :obj:`str`
            The string indicating the way to calculate the diffusion coefficient.
        """
        self.options = [
            "EXPLICIT",
            "TKEB"
        ]

    def check(self):
        pass


class ExplicitCoefficient(Number):
    """The setting for the explicit value of the diffusion coefficient.

    Inherits from :class:`~.Number`.
    """
    @Terminus.assign
    def __init__(self, value: float):
        """The constructor for the :class:`~.ExplicitCoefficient` class.

        Parameters
        ----------
        value : :obj:`float`
            The float value that is being checked.
        """
        self.type = float

    def check(self):
        """Abstract method from :class:`~.Terminus`.
        Raises
        ------
        ValueError
            If the value isn't greater than 1e-3.
        """
        self.lower_bound(1e-3)


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
        """The constructor for the :class:`~.TKEB` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the TKEB
            equation.
        """
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
        """The constructor for the :class:`~.TKEB` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the TKEB
            equation.
        """
        self.quantity = NonNegativeInteger
        self.max_error = Percentage


class ContourPlots(Settings):
    """The :class:`~.ContourPlots` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    output : :obj:`bool`
        Whether or not we output the contour plots.

    concentration: :obj:`bool`
        Show contour plots of the concentration value.

    exposure: :obj:`bool`
        Show the contour plots of the exposure value.

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
        """The constructor for the :class:`~.ContourPlots` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the contour plots.
        """
        self.output = bool
        self.concentration = bool
        self.exposure = bool
        self.creation_frequency = NonNegativeFloat
        self.number_of_contours = NonNegativeInteger
        self.range = RangeMode
        self.scale = ScaleType 
        self.contours = ManualContours


class RangeMode(StringSelection):
    """The contour range mode selection setting class.

    It inherits from :class:`~.StringSelection`.

    """
    @Terminus.assign
    def __init__(self, value: str):
        """The constructor for the :class:`RangeMode` class.

        value : :obj:`str`
            The string indicating the range mode selection.
        """
        self.options = [
            "auto",
            "manual"
        ]

    def check(self):
        pass


class ScaleType(StringSelection):
    """The contour scale type selection setting class.

    It inherits from :class:`~.Terminus`.

    """
    @Terminus.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`ScaleType` class.

        value : :obj:`str`
            The string indicating the scale type selection.
        """
        self.options = [
            "linear",
            "logarithmic"
        ]

    def check(self):
        pass


class Points(Dict):

    """The :class:`~.Points` class. It inherits from
    :class:`~.Dict`.

    Attributes
    ---------
    type: :class:`~.Point`
        Path to the dictionary of values for the points to be monitored

    """
    @Dict.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.Points` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the points to be monitored.

        """
        self.type = Point


class Lines(Dict):

    """The :class:`~.Lines` class. It inherits from
    :class:`~.Dict`.

    Attributes
    ---------
    type: :class:`~.Line`
        Path to the dictionary of lines to be monitored.

    """
    @Dict.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.Lines` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the lines to be monitored.

        """
        self.type = Line


class Line(Settings):
    """The :class:`~.Line` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    pointA: :class:`~.Point`
        The first of two points defining the line in 3D space.

    pointB: :class:`~.Point`
        The second of two points defining the line in 3D space.

    """
    @Settings.assign
    def __init__(self, value: dict):
        """The constructor for the :class:`~.Line` class.

        Parameters
        ----------
        value : :obj:`dict`
            The values corresponding to each line.
        """
        self.pointA = Point
        self.pointB = Point


class Planes(Dict):
    """The :class:`~.Planes` class. It inherits from
    :class:`~.Dict`.

    Attributes
    ---------
    type: :class:`~.Plane`
        Path to the dictionary of planes to be monitored.
    """
    @Dict.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`~.Planes` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the planes to be monitored.

        """
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
        """The constructor for the :class:`~.Plane` class.

        Parameters
        ----------
        value : :obj:`dict`
            The values corresponding to each plane.
        """
        self.axis = Axis
        self.distance = NonNegativeFloat


class Axis(StringSelection):
    """The axis selection setting class.

    It inherits from :class:`~.Terminus`.

    """
    @Terminus.assign
    def __init__(self, value: str):
        """The constructor for the :class:`Axis` class.

        value : :obj:`str`
            The string indicating the axis.
        """
        self.options = [
            "xy",
            "yz",
            "xz"
        ]

    def check(self):
        pass


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
        """The constructor for the :class:`~.ManualContours` class.

        Parameters
        ----------
        value : :obj:`dict`
            The values corresponding to manual contours.
        """
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
        """The constructor for the :class:`~.WellMixed` class.

        Parameters
        ----------
        value : :obj:`dict`
            The values corresponding to well mixed model.
        """
        self.volume = NonNegativeFloat


class Percentage(Number):
    """The :class:`~.Percentage` class. It inherits from
    :class:`~.Number`.

    Attributes
    ---------
    type :obj:`float`
        The float value corresponding to a percentage.
    """
    @Terminus.assign
    def __init__(self, value: float):
        """The constructor for the :class:`~.Percentage` class.

        Parameters
        ----------
        value : :obj:`float`
            The float value that is being checked.
        """
        self.type = float

    def check(self):
        """Abstract method from :class:`~.Terminus`.
        Raises
        ------
        ValueError
            If the value doesn't lie within the bounds.
        """
        self.lower_bound(0.0)
        self.upper_bound(100.0)


class NonNegativeFloat(Number):
    """The :class:`~.NonNegativeFloat` class. It inherits from
    :class:`~.Number`.

    """
    @Terminus.assign
    def __init__(self, value: float):
        """The constructor for the :class:`~.NonNegativeFloat` class.

        Parameters
        ----------
        value : :obj:`float`
            The float value that is being checked.
        """
        self.type = float

    def check(self):
        """Abstract method from :class:`~.Terminus`.
        Raises
        ------
        ValueError
            If the value isn't greater than 0.
        """
        self.lower_bound(0.0)


class NonNegativeInteger(Number):
    """The :class:`~.NonNegativeInteger` class. It inherits from
    :class:`~.Number`.


    """
    @Terminus.assign
    def __init__(self, value: float):
        """The constructor for the :class:`~.NonNegativeInteger` class.

        Parameters
        ----------
        value : :obj:`float`
            The float value that is being checked.
        """
        self.type = int

    def check(self):
        """Abstract method from :class:`~.Terminus`.

        Raises
        ------
        ValueError
            If the value isn't greater than 0.
        """
        self.lower_bound(0)
