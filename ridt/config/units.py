from typing import Iterable

from .ridtconfig import RIDTConfig

R = 8.3145 # Universal Gas Constant
D = 1.292 # Density of air at room temperature kg.m-3


class Units:
    """The class that perfoms all unit conversions throughout RIDT.

    Attributes
    ----------
    time : :obj:`str`
        The string representation of the selected time units.

    mass : :obj:`str`
        The string representation of the selected mass units.
    
    concentration : :obj:`str`
        The string representation of the selected concentration units.

    exposure : :obj:`str`
        The string representation of the selected exposure units.

    space: :obj:`str`
        The string representation of the selected spatial units.
    
    concentration_si : :obj:`str`
        The string representation of the SI concentration units.

    exposure_si : :obj:`str`
        The string representation of the SI exposure units.
    
    temperature : :obj:`float`
        The temperature value.
    
    pressure : :obj:`float`
        The pressure value.
    
    molecular_weight : :obj:`float`
        The material's molecular weight value.
    
    nmol : obj:`float`
        The number of moles of gas per unit volume.

    """
    def __init__(self, setting: RIDTConfig):
        """The constructor for the :class:`Units` class.

        Parameters
        ----------
        setting : :class:`~.RIDTConfig`
            The settings object containing the units selections and definitions. 

        """
        self.time = setting.time_units
        self.mass = setting.mass_units
        self.concentration = setting.concentration_units
        self.exposure = setting.exposure_units
        self.space = setting.spatial_units
        self.concentration_si = "kg.m-3"
        self.exposure_si = "kg.s.m-3"
        self.temperature = setting.physical_properties.temperature
        self.pressure = setting.physical_properties.pressure
        self.molecular_weight = setting.physical_properties.agent_molecular_weight
        self.nmol = self.pressure / (self.temperature * R)

    @property
    def concentration_factor(self) -> float:
        """The conversion factor for provided concentration into SI units.

        This function will compute the scaling factor for the concentration
        quantities to and from SI units. This is because all calculations RIDT
        performs internally are in SI units.

        Returns
        -------
        :obj:`float`
            The unit conversion factor.

        Raises
        ------
        :obj:`ValueError`
            If the concentration units provided are not valid.

        """
        if self.concentration == "kg.m-3":
            return 1.0
        elif self.concentration == "kg.kg-1":
            return 1 / D
        elif self.concentration == "mg.m-3":
            return 1e-6
        elif self.concentration == "ppm":
            return (self.molecular_weight * self.nmol) * 1e-6
        elif self.concentration == "ppb":
            return (self.molecular_weight * self.nmol) * 1e-9
        elif self.concentration == "ppt":
            return (self.molecular_weight * self.nmol) * 1e-12
        else:
            raise ValueError(f"{self.concentration} not a valid unit")

    @property
    def exposure_factor(self):
        """The conversion factor for provided exposure into SI units.

        This function will compute the scaling factor for the exposure
        quantities to and from SI units. This is because all calculations RIDT
        performs internally are in SI units.

        Returns
        -------
        :obj:`float`
            The unit conversion factor.

        Raises
        ------
        :obj:`ValueError`
            If the exposure units provided are not valid.

        """
        if self.exposure == "kg.s.m-3":
            return 1.0
        elif self.exposure == "mg.min.m-3":
            return 1e-6 * 60
        else:
            raise ValueError(f"{self.exposure} not a valid unit")

    def concentration_converter(self, values: Iterable[float]):
        """Converts all concentration values in iterable to SI units.

        Parameters
        ----------
        values : :obj:`Iterable`[:obj:`float`]
            The iterable of values to be converted.

        Returns
        -------
        :obj:`Iterable`[:obj:`float`]
            A new iterable containing the scaled values.
        """
        return [v * self.concentration_factor for v in values]

    def exposure_converter(self, values: Iterable):
        """Converts all exposure values in iterable to SI units.

        Parameters
        ----------
        values : :obj:`Iterable`[:obj:`float`]
            The iterable of values to be converted.

        Returns
        -------
        :obj:`Iterable`[:obj:`float`]
            A new iterable containing the scaled values.
        """
        return [v * self.exposure_factor for v in values]
