import sys

import math

from ridt.base import Settings
from ridt.base import Terminus
from ridt.base import List
from ridt.base import Dict
from ridt.base import Number
from ridt.base import StringSelection
from ridt.base import Error
from ridt.base import ConsistencyError

import warnings

def custom_formatwarning(msg, *args, **kwargs):
    return "Warning: " + str(msg) + '\n'

warnings.formatwarning = custom_formatwarning

class RIDTConfig(Settings):
    """The settings object for ridt.

    This takes a dictionary and checks that all relevant information exists
    in the dictioary.

    Attributes
    ----------
    well_mixed : :obj:`bool`
        The flag indicating whether to evaluate the well mixed model.

    eddy_diffusion: :obj:`bool`
        The flag indicating whether to evaluate the eddy diffusion model.
    
    compute_exposure: :obj:`bool`
        The flag indicating whether to compute and perfom analysis on the
        exposure.

    write_data_to_csv: :obj:`bool`
        The flag indicating whether to write all computed data to csv files, in
        addition to the numpy bindary arrays (*.npy).

    time_units : :class:`~.TimeUnits`
        The temporal units selection.
    
    time_samples : :class:`~.NonNegativeInteger`
        The temporal discretisation.
    
    total_time : :class:`~.NonNegativeFloat`
        The total time for the simulation.
    
    dimensions : :class:`~.Dimensions`
        The spatial bounds of the system.
    
    spatial_samples : :class:`~.SpatialSamples`
        The spatial discretisation of the system.

    spatial_units : :class:`~.SpatialUnits`
        The spatial units selection.

    physical_properties : :class:`~.PhysicalProperties`
        The physical properties of the system.
    
    concentration_units : :class:`~.ConcentrationUnits`
        The concentration units selection.
    
    exposure_units : :class:`~.ExposureUnits`
        The exposure units selection.
    
    mass_units : :class:`~.MassUnits`
        The mass units selection.
    
    fresh_air_change_rate : :class:`~.FreshAirChangeRate`
        The fresh air change rate.

    fresh_air_change_rate_units : :class:`~.FreshAirChangeRateUnits`
        The fresh air change rate unit selection.
    
    modes : :class:`~.Modes`
        Source settings.
    
    thresholds : :class:`~.Thresholds`
        Threshold settings.
    
    models : :class:`~.Models`
        Model specific settings.

    Parameters
    ----------
    value : :obj:`dict`
        The dictionary of values to be verified and stored.

    Raises
    ------
    
    """

    @Settings.assign
    def __init__(self, values: dict):
        """The RIDTConfig initaliser

        Parameters
        ----------
        value : :obj:`dict`
            The dictionary of values to be verified and stored.


        """
        self.well_mixed = bool
        self.eddy_diffusion = bool
        self.compute_exposure = bool
        self.write_data_to_csv = bool

        self.integration_method = IntegrationMethod

        self.time_units = TimeUnits
        self.time_samples = TimeSamples
        self.total_time = NonNegativeFloat

        self.dimensions = Dimensions
        self.spatial_samples = SpatialSamples

        self.spatial_units = SpatialUnits
        self.physical_properties = PhysicalProperties
        self.concentration_units = ConcentrationUnits
        self.exposure_units = ExposureUnits
        self.mass_units = MassUnits

        self.fresh_air_change_rate_units = FreshAirChangeRateUnits
        self.fresh_air_change_rate = NonNegativeFloat 

        self.modes = ModeSettings
        self.thresholds = Thresholds

        self.models = ModelSettings

    def consistency_check(self):
        """Verifies the self consistency of the settings object.

        Returns
        -------
        None

        Raises
        ------
        :class:`~.ConsistencyError
            If any sources lie outside the simulation domain.
        :class:`~.ConsistencyError
            If any sources' release times are outside the simulation domain.
        :class:`~.ConsistencyError
            If any monitor locations are outside of the simulation domain.
        :class:`~.ConsistencyError
            If more than 5 thresholds of a given type are defined.
        :class:`~.ConsistencyError
            If the number of a given type of plots requested is greater than
            the time discretisation.

        """

        for mode in ["instantaneous", "infinite_duration", "fixed_duration"]:
            for key, value in getattr(self.modes, mode).sources.items():
                dim = self.dimensions
                for axis in ["x", "y", "z"]:
                    par = getattr(value, axis)
                    bound = getattr(dim, axis)
                    if isinstance(par, list):
                        for item in par:
                            if item < 0 or item > bound:
                                raise ConsistencyError(
                            f"{mode} source {key} x position is "
                            f"outside space domain (0, {bound}).")
                    else:
                        if par < 0 or par > bound:
                            raise ConsistencyError(
                        f"{mode} source {key} x position is "
                        f"outside space domain (0, {bound}).")

        for mode in ["instantaneous", "infinite_duration"]:
            for key, value in getattr(self.modes, mode).sources.items():
                if isinstance(value.time, list):
                    for item in value.time:
                        if item > self.total_time:
                            raise ConsistencyError(
                        f"{mode} source {key} time is "
                        f"outside time domain [0, {self.total_time}).")
                else:
                    if value.time > self.total_time:
                        raise ConsistencyError(
                    f"{mode} source {key} time is "
                    f"outside time domain [0, {self.total_time}).")

        for key, value in getattr(self.modes, "fixed_duration").sources.items():
            if isinstance(value.start_time, list):
                for item in value.start_time:
                    if item > self.total_time:
                        raise ConsistencyError(
                    f"{mode} source {key} start time is "
                    f"outside time domain [0, {self.total_time}).")
            else:
                if value.start_time > self.total_time:
                    raise ConsistencyError(
                f"{mode} source {key} start time is "
                f"outside time domain [0, {self.total_time}).")

            if isinstance(value.end_time, list):
                for item in value.end_time:
                    if item > self.total_time:
                        raise ConsistencyError(
                    f"{mode} source {key} end time is "
                    f"outside time domain [0, {self.total_time}).")
            else:
                if value.end_time > self.total_time:
                    raise ConsistencyError(
                f"{mode} source {key} end time is "
                f"outside time domain [0, {self.total_time}).")
        
        dims = ["x", "y", "z"]
        for plane in self.models.eddy_diffusion.monitor_locations.planes.values():
            dim = [axis for axis in dims if axis not in str(plane.axis)][0]
            if isinstance(plane.distance, list):
                if max(plane.distance) > getattr(self.dimensions, dim):
                    raise ConsistencyError(f"{plane} is outside the space domain")
            else:
                if plane.distance > getattr(self.dimensions, dim):
                    raise ConsistencyError(f"{plane} is outside the space domain")

        for key, point in self.models.eddy_diffusion.monitor_locations.points.items():
            for dim in dims:
                if getattr(point, dim) > getattr(self.dimensions, dim):
                    raise ConsistencyError(
                f"{key}'s {dim} value, is outside space domain "
                f"(0, {getattr(self.dimensions, dim)})")

        for key, line in self.models.eddy_diffusion.monitor_locations.lines.items():
            for dim in dims:
                if getattr(line.point, dim) > getattr(self.dimensions, dim):
                    raise ConsistencyError(
                f"{key}'s {dim} value, is outside space domain "
                f"(0, {getattr(self.dimensions, dim)})")

        thresh = self.thresholds
        if len(thresh.concentration) > 5 or len(thresh.exposure) > 5:
            raise ConsistencyError(f"Cannot exceed more than 5 thresholds")
 
        line_number = self.models.eddy_diffusion.lines_plots.number
        if isinstance(line_number, list):
            for item in line_number:
                if item > self.time_samples:
                    raise ConsistencyError(
                f"The number of requrested line plots ({point_number}) cannot exceed the "
                f"number of time samples ({self.time_samples}).")
        else:
            if line_number > self.time_samples:
                raise ConsistencyError(
            f"The number of requrested line plots ({line_number}) cannot exceed the "
            f"number of time samples ({self.time_samples}).")
 
        contour_number = self.models.eddy_diffusion.planes_plots.number
        if isinstance(contour_number, list):
            for item in contour_number:
                if item > self.time_samples:
                    raise ConsistencyError(
                f"The number of requrested contour plots ({item}) cannot exceed the "
                f"number of time samples ({self.time_samples}.)")
        else:
            if contour_number > self.time_samples:
                raise ConsistencyError(
            f"The number of requrested contour plots ({contour_number}) cannot exceed the "
            f"number of time samples ({self.time_samples}).")

class TimeSamples(Number):
    """The :class:`~.TimeSamples` class. It inherits from
    :class:`~.Number`.

    """
    @Terminus.assign
    def __init__(self, value: int):
        """The constructor for the :class:`~.TimeSamples` class.

        Parameters
        ----------
        value : :obj:`int`
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
        self.lower_bound_exclusive(1)


class PhysicalProperties(Settings):
    """The physical properties settings object.

    Attributes
    ----------
    agent_molecular_weight_units : :class:`~.AgentMolecularWeightUnits`
        The agent molecular weight units selection.

    agent_molecular_weight : :class:`~.AgentMolecularWeight`
        The agent molecular weight.
    
    pressure_units : :class:`~.PressureUnits`
        The pressure units selection.

    pressure: :class:`~.Pressure`
        The pressure of the atmosphere.
    
    temperature_units : :class:`~.TemperatureUnits`
        The temperature units selection.

    temperature: :class:`~.Temperature`
        The temperature of the atmosphere.

    """
    @Settings.assign
    def __init__(self, values: dict):
        """The PhysicalProperties initialiser

        Parameters
        ----------
        value : :obj:`dict`
            The dictionary of values to be verified and stored.

        """
        self.agent_molecular_weight_units = AgentMolecularWeightUnits
        self.agent_molecular_weight = NonNegativeFloat 
        self.pressure_units = PressureUnits
        self.pressure = NonNegativeFloat
        self.temperature_units = TemperatureUnits
        self.temperature = NonNegativeFloat


class AgentMolecularWeightUnits(StringSelection):
    """The agent molecular weights units selection class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, value: str):
        """The AgentMolecularWeightUnits class initialiser

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "mol.m-3"
        ]
    
    def check(self):
        pass
    
class IntegrationMethod(StringSelection):
    """The integration methods selection class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, value: str):
        """The IntegrationMethod class initialiser

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "cumulativetrapezoidal",
            "romberg"
        ]
    
    def check(self):
        pass
 

class PressureUnits(StringSelection):
    """The pressure units selection class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, value: str):
        """The PressureUnits class initialiser.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "Pa"
        ]
    
    def check(self):
        pass


class TemperatureUnits(StringSelection):
    """The temperature units selection class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, value: str):
        """The TemperatureUnits class initialiser.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "K"
        ]
    
    def check(self):
        pass



class FreshAirChangeRate(Number):
    """The FreshAirChangeRate class

    Stores the value of the fresh air change rate.

    """

    @Terminus.assign
    def __init__(self, value: float):
        self.type = float

    
    def check(self):
        """Checks that the value is in the required bounds.

        """
        self.lower_bound(5e-4)
        self.upper_bound(5e2)


class DispersionModel(StringSelection):
    """The dispersion model selection setting class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, value: str):
        """The DispersionModel class initialiser.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "eddy_diffusion",
            "well_mixed"
        ]

    def check(self):
        pass


class ReleaseType(StringSelection):
    """The release type selection setting class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, valu: str):
        """The ReleaseType class initialiser.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

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

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, valu: str):
        """The TimeUnits class initialiser.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "s",
        ]

    def check(self):
        pass


class ConcentrationUnits(StringSelection):
    """The time units selection setting class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, valu: str):
        """The ConcentrationUnits class initialiser.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "kg.m-3",
            "kg.kg-1",
            "mg.m-3",
            "ppm",
            "ppb",
            "ppt"
        ]
    def check(self):
        pass


class ExposureUnits(StringSelection):
    """The time units selection setting class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, valu: str):
        """The ExposureUnits class initialiser.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "mg.min.m-3",
            "kg.s.m-3"
        ]

    def check(self):
        pass


class SpatialUnits(StringSelection):
    """The time units selection setting class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, valu: str):
        """The SpatialUnits class initialiser.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "m",
        ]

    def check(self):
        pass


class MassUnits(StringSelection):
    """The mass units selection setting class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, valu: str):
        """The MassUnits class initialiser.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "kg",
        ]

    def check(self):
        pass


class FreshAirChangeRateUnits(StringSelection):
    """The fresh air change rate units selection setting class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, valu: str):
        """The FreshAirChangeRateUnits class initialiser.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "m3.s-1",
        ]

    def check(self):
        pass


class ModelSettings(Settings):
    """The Model Settings class.

    Attributes
    ----------
    eddy_diffusion: :class:`~.EddyDiffusion`
        The  eddy diffusion model settings.


    """
    @Settings.assign
    def __init__(self, values: dict):
        """The ModelSettings class initialiser.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary corresponding to the instantaneous
            settings configurations.
        """
        self.eddy_diffusion = EddyDiffusion


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
        """The ModeSettings class initialiser.

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
        """The InstantaneousSettings class initialiser.

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
        """The InstantaneousSource class initialiser.

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


class InstantaneousReleaseMass(Number):
    """The instantaous release mass setting.

    Container the value of an instantaneous release mass.

    """
    @Terminus.assign
    def __init__(self, value: float):
        self.type = float

    def check(self):
        self.lower_bound(1e-6)
        self.upper_bound(10.0)

class ReleaseRate(Number):
    """The release rate setting.

    Contains the value for the rate of release for a source.
    
    """
    @Terminus.assign
    def __init__(self, value: float):
        self.type = float

    def check(self):
        self.lower_bound(1e-6)
        self.upper_bound(10.0)

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
        """The InfiniteDurationSettings class initialiser.

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
        """The InfiniteDurationSourceDict  class initialiser.

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
        values : :obj:`list`
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

    planes_plots: :class:`~.ContourPlots`
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
        self.monitor_locations = MonitorLocations
        self.coefficient = Coefficient
        self.images = Images
        self.analysis = AnalysisSettings
        self.planes_plots = ContourPlots
        self.lines_plots = LinePlots
        self.points_plots = PointPlots


class AnalysisSettings(Settings):
    """The analysis settings 

    Attributes
    ----------
    perform_analysis: :obj:`bool`
        Whether perform analysis or not.

    percentage_exceedance : :class:`~.Percentage`
        The percentage which must be exceeded in percent exceed threshold
        calcluations.
    
    exclude_uncertain_values: :obj:`bool`
        Whether to exclude values within 2m of any source from analysis.

    """
    @Settings.assign
    def __init__(self, values: dict):
        """The AnalysisSettings class initialiser.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the eddy diffusion
            model type.

        """
 
        self.perform_analysis = bool
        self.percentage_exceedance = Percentage
        self.exclude_uncertain_values = bool



class LinePlots(Settings):
    """The :class:`~.LinePlots` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ----------
    output : :obj:`bool`
        Whether or not we output line plots.

    """
    @Settings.assign
    def __init__(self, values: dict):
        self.output = bool
        self.animate = bool
        self.scale = ScaleType
        self.number = PositiveInt 


class PointPlots(Settings):
    """The :class:`~.PointPlots` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ----------
    output : :obj:`bool`
        Whether or not we output point plots.

    """
    @Settings.assign
    def __init__(self, values: dict):
        self.output = bool
        self.scale = ScaleType


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
        self.evaluate = EvaluateFlags
        self.points = Points
        self.lines = Lines
        self.planes = Planes
        self.domain = FullDomain
    
    def consistency_check(self):
        for item in self.evaluate.keys():
            if item not in self.__dict__:
                raise ConsistencyError(f"{item} is not a type if monitor location")

class EvaluateFlags(Dict):

    @Settings.assign
    def __init__(self, values: dict):
        self.type = bool

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
        self.x = PositiveFloat 
        self.y = PositiveFloat 
        self.z = PositiveFloat


class Length(Number):
    @Terminus.assign
    def __init__(self, value: float):
        self.type = float

    def check(self):
        self.lower_bound(2)
        self.upper_bound(100)


class Width(Number):
    @Terminus.assign
    def __init__(self, value: float):
        self.type = float

    def check(self):
        self.lower_bound(2)
        self.upper_bound(100)


class Height(Number):
    @Terminus.assign
    def __init__(self, value: float):
        self.type = float

    def check(self):
        self.lower_bound(2)
        self.upper_bound(20)


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
        self.x = SpatialDiscretisation 
        self.y = SpatialDiscretisation
        self.z = SpatialDiscretisation


class SpatialDiscretisation(Number):
    @Terminus.assign
    def __init__(self, value: int):
        self.type = int
    
    def check(self):
        self.lower_bound(2)


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

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`CoefficientMode` class.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

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
        self.upper_bound(1.0)


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
        self.bound = TKEBBound
        self.total_air_change_rate = TotalAirChangeRate 
        self.number_of_supply_vents = NumberOfSupplyVents 


class TKEBBound(StringSelection):
    """The TKEB bound selection class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.
    
    """
    @Terminus.assign
    def __init__(self, values: dict):
        """The TKEBBound class initialiser.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.
        
        """
        self.options = [
            "lower",
            "regression",
            "upper"
        ]

    def check(self):
        pass



class TotalAirChangeRate(Number):
    """Total air change rate settings

    Contains the value of the total air change rate.

    """
    @Terminus.assign
    def __init__(self, value: float):
        self.type = float

    def check(self):
        self.lower_bound(5e-4)
        self.upper_bound(5e2)


class NumberOfSupplyVents(Number):
    """Number of supply vents.

    Contains the number of supply vents.

    """
    @Terminus.assign
    def __init__(self, value: int):
        self.type = int 

    def check(self):
        self.lower_bound(1)
        self.upper_bound(50)


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
        self.mode = ImageMode
        self.quantity = ImageSourceNumber 


class ImageSourceNumber(Number):
    @Terminus.assign
    def __init__(self, value: int):
        self.type = int
    
    def check(self):
        self.lower_bound(0)
        self.upper_bound(20)

class ImageMode(StringSelection):
    """The image mode selection

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`ImageMode` class.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "manual",
            "auto"
        ]

    def check(self):
        pass



class ContourPlots(Settings):
    """The :class:`~.ContourPlots` class. It inherits from
    :class:`~.Settings`.

    Attributes
    ---------
    output : :obj:`bool`
        Whether or not we output the contour plots.

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
        self.animate = bool
        self.number = PositiveInt 
        self.number_of_contours = NonNegativeInteger
        self.range = RangeMode
        self.scale = ScaleType 
        self.contours = ManualContours
    
    def consistency_check(self):
        if self.contours.min >= self.contours.max:
            raise ConsistencyError(
                f"contour min ({self.contours.min})"
                f" >= contour max ({self.contours.max})")


class RangeMode(StringSelection):
    """The contour range mode selection setting class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, value: str):
        """The constructor for the :class:`RangeMode` class.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "auto",
            "manual"
        ]

    def check(self):
        pass


class ScaleType(StringSelection):
    """The contour scale type selection setting class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, values: dict):
        """The constructor for the :class:`ScaleType` class.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

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
    start_point: :class:`~.Point`
        The location of the start of the line in 3D space.

    length: :class:`~.Point`
        The length of the line in 3D space.

    direction: :obj:`str`
        The axis in which the line extends.

    """
    @Settings.assign
    def __init__(self, value: dict):
        """The constructor for the :class:`~.Line` class.

        Parameters
        ----------
        value : :obj:`dict`
            The values corresponding to each line.
        """
        self.point = Point
        self.parallel_axis = ParallelAxis


class ParallelAxis(StringSelection):
    """The parallel axis selection setting class.

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, value: str):
        """The constructor for the :class:`ParallelAxis` class.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

        """
        self.options = [
            "x",
            "y",
            "z"
        ]

    def check(self):
        pass


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


class FullDomain(Dict):
    """The :class:`~.FullDomain` class. It inherits from
    :class:`~.Dict`.

    Attributes
    ---------
    type: :obj:`bool`
        The boolean value to idicate whether to evaluate the domain.
    """
    @Dict.assign
    def __init__(self, value: bool):
        """The constructor for the :class:`~.FullDomain` class.

        Parameters
        ----------
        values : :obj:`dict`
            The values corresponding to the domain to be monitored.

        """
        self.type = bool 



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

    Attributes
    ----------
    options : :obj:`list` [:obj:`str`]
        The list of allowed options.

    """
    @Terminus.assign
    def __init__(self, value: str):
        """The constructor for the :class:`Axis` class.

        Parameters
        ----------
        value : :obj:`str`
            The chosed value.

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
        self.min = PositiveFloat 
        self.max = PositiveFloat


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


class PositiveFloat(Number):
    """The :class:`~.PositiveFloat` class. It inherits from
    :class:`~.Number`.

    """
    @Terminus.assign
    def __init__(self, value: float):
        """The constructor for the :class:`~.PositiveFloat` class.

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
        self.lower_bound_exclusive(0.0)

class PositiveInt(Number):
    """The :class:`~.PositiveInt` class. It inherits from
    :class:`~.Number`.

    """
    @Terminus.assign
    def __init__(self, value: int):
        """The constructor for the :class:`~.PositiveInt` class.

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
        self.lower_bound_exclusive(0)




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
