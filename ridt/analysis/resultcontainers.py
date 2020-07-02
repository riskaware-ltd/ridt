from typing import Tuple

from ridt.container import Domain

from ridt.config import RIDTConfig
from ridt.config import Units


class ResultContainer:
    """A base class for all results containers.

    Attributes
    ----------
    setting : :class:`~.RIDTConfig`
        The settings for the run in question.
    
    geometry : :obj:`str`
        The geometry domain this result corresponds to.

    id : :obj:`str`
        The id of the domain this result corresponds to.
    
    domain : :class:`~.Domain`
        The instance of :class:`~.Domain` corresponding to :attr:`setting`.

    quantity: :obj:`str`
        The string id for the quantity stored in the data  store.

    units : :class:`~.Units`
        The instance of :class:`~.Units` corresponding to :attr:`setting`.

    """


    def __init__(self, setting: RIDTConfig, geometry: str, id: str, quantity: str):
        self.setting = setting
        self.geometry = geometry
        self.id = id
        self.quantity = quantity
        self.units = Units(setting)
        self.domain = Domain(setting)
    
    def same_geometry(self, other):
        """Checks if item has same :attr:`geometry`.

        Parameters
        ----------
        other
            The comparative item.

        Raises
        ------
        :obj:`ValueError`
            if the :attr:`geometry` attributes are different.
        """
        if self.geometry != other.geometry:
            raise ValueError("You are comparing two different geometries.")
    
    @property
    def unit(self):
        """:obj:`str` The units corresponding :attr:`quantity`.

        """
        return getattr(self.units, f"{self.quantity}")
    

class Maximum(ResultContainer):
    """Result container for the max value in a domain.

    Attributes
    ----------
    index : Tuple[:obj:`int`]
        The index in the array where the maximum ocurred.

    value : :obj:`float`    
        The value of the maximum.

    """

    def __init__(self,
                 setting: RIDTConfig,
                 geometry: str,
                 id: str,
                 quantity: str,
                 index: Tuple[int],
                 value: float):
        """The Maximum class initialiser

        Parameters
        ----------
        setting : :class:`~.RIDTConfig`
            The settings for the run in question.
        
        geometry : :obj:`str`
            The geometry domain this result corresponds to.

        id : :obj:`str`
            The id of the domain this result corresponds to.
        
        quantity: :obj:`str`
            The string id for the quantity stored in the data  store.

        index : Tuple[:obj:`int`]
            The index in the array where the maximum ocurred.
    
        value : :obj:`float`    
            The value of the maximum.

        """
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
        """:obj:`str` : The string representation of the result.

        """
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
        """:obj:`list` [:obj:`str`] : The list of headers for a csv output.

        """
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
        """:obj:`list` [:obj:`float`] : The list of values for a csv output.

        """
        factor = getattr(self.units, f"{self.quantity}_factor")
        if self.index:
            t, x, y, z = self.domain.values(self.geometry, self.id, self.index)
            return [self.id, t, x, y, z, self.value / factor]
        else:
            return [self.id, "None", "None", "None", "None"]
    
    @property
    def fname(self):
        """:obj:`str` : the file name for the this result output.

        """
        return f"{self.geometry}_maximums.csv"

    @property
    def title(self):
        """:obj:`str` : the title string for this result.

        """
        return "Maxima"

    @property
    def extreme_title(self):
        """:obj:`str` : the extremum version of the title for this result.

        """
        return f"Maxium value for {self.geometry}:"
    
    @property
    def valid(self):
        """:obj:`bool` : Returns true if contains valid index, else false.

        """
        if self.index and self.value != "nan":
            return True
        else:
            return False
    

class Exceedance(ResultContainer):
    """Result container for the threshold exceedance in a domain.

    Attributes
    ----------
    index : Tuple[:obj:`int`]
        The index in the array where the exceedance ocurred.

    threshold : :obj:`float`
        The threshold that was exceeded.

    """

    def __init__(self,
                 setting: RIDTConfig,
                 geometry: str,
                 id: str,
                 quantity: str,
                 index: Tuple[int],
                 threshold: float):
        """The Exceedance class initialiser

        Parameters
        ----------
        setting : :class:`~.RIDTConfig`
            The settings for the run in question.
        
        geometry : :obj:`str`
            The geometry domain this result corresponds to.

        id : :obj:`str`
            The id of the domain this result corresponds to.
        
        quantity: :obj:`str`
            The string id for the quantity stored in the data  store.

        index : Tuple[:obj:`int`]
            The index in the array where the exceedance ocurred.
    
        threshold : :obj:`float`
            The threshold that was exceeded.

        """
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
        """:obj:`str` : The string representation of the result.

        """
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
        """:obj:`list` [:obj:`str`] : The list of headers for a csv output.

        """
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
        """:obj:`list` [:obj:`float`] : The list of values for a csv output.

        """
        if self.index:
            t, x, y, z = self.domain.values(self.geometry, self.id, self.index)
            return [self.id, t, x, y, z]
        else:
            return [self.id, "None", "None", "None"]
    
    @property
    def fname(self):
        """:obj:`str` : the file name for the this result output.

        """
        return f"{self.geometry}_exceeds_{self.threshold}{self.unit}.csv"

    @property
    def title(self):
        """:obj:`str` : the title string for this result.

        """
        return "Threshold Exceedance"
    
    @property
    def extreme_title(self):
        """:obj:`str` : the extremum version of the title for this result.

        """
        return f"Minimum time to {self.threshold}{self.unit} for {self.geometry}:"
    
    @property
    def valid(self):
        """:obj:`bool` : Returns true if contains valid index, else false.

        """
        return True if self.index else False

class PercentExceedance(ResultContainer):
    """Result container for the percent threshold exceedance in a domain.

    Attributes
    ----------
    index : :obj:`int`
        The time index in the array where the exceedance ocurred.

    threshold : :obj:`float`
        The threshold that was exceeded.
    
    percent : :obj:`float`
        The percentage by which the threshold was exceeded

    """

    def __init__(self,
                 setting: RIDTConfig,
                 geometry: str,
                 id: str,
                 quantity: str,
                 index: int,
                 threshold: float,
                 percent: float):
        """The PercentExceedance class initialiser

        Parameters
        ----------
        setting : :class:`~.RIDTConfig`
            The settings for the run in question.
        
        geometry : :obj:`str`
            The geometry domain this result corresponds to.

        id : :obj:`str`
            The id of the domain this result corresponds to.
        
        quantity: :obj:`str`
            The string id for the quantity stored in the data  store.

        index : :obj:`int`
            The time index in the array where the exceedance ocurred.
    
        threshold : :obj:`float`
            The threshold that was exceeded.

        percent : :obj:`float`
            The percentage by which the threshold was exceeded

        """
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
        """:obj:`str` : The string representation of the result.

        """
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
        """:obj:`list` [:obj:`str`] : The list of headers for a csv output.

        """
        return [
            "id",
            f"time ({self.units.time})",
        ]

    @property
    def row(self):
        """:obj:`list` [:obj:`float`] : The list of values for a csv output.

        """
        if self.index:
            t = self.domain.time[self.index]
            return [self.id, t]
        else:
            return [self.id, "None"]
    
    @property
    def fname(self):
        """:obj:`str` : the file name for the this result output.

        """
        return f"{self.geometry}_exceeds_{self.threshold}{self.unit}.csv"
    
    @property
    def title(self):
        """:obj:`str` : the title string for this result.

        """
        return f"{self.percent}% Threshold Exceedance"

    @property
    def extreme_title(self):
        """:obj:`str` : the extremum version of the title for this result.

        """
        return f"Minimum time to {self.threshold}{self.unit} for "\
               f"{self.percent}% of domain for {self.geometry}:"

    @property
    def valid(self):
        """:obj:`bool` : Returns true if contains valid index, else false.

        """
        return True if self.index else False

class MaxPercentExceedance(ResultContainer):
    """Result container for the max percent threshold exceedance in a domain.

    Attributes
    ----------
    index : :obj:`int`
        The time index in the array where the exceedance ocurred.

    threshold : :obj:`float`
        The threshold that was exceeded.
    
    value : :obj:`float`
        The percentage by which the threshold was exceeded


    """
    def __init__(self,
                 setting: RIDTConfig,
                 geometry: str,
                 id: str,
                 quantity:str,
                 value: float,
                 index: int,
                 threshold: float):
        """The PercentExceedance class initialiser

        Parameters
        ----------
        setting : :class:`~.RIDTConfig`
            The settings for the run in question.
        
        geometry : :obj:`str`
            The geometry domain this result corresponds to.

        id : :obj:`str`
            The id of the domain this result corresponds to.
        
        quantity: :obj:`str`
            The string id for the quantity stored in the data  store.

        index : :obj:`int`
            The time index in the array where the exceedance ocurred.
    
        threshold : :obj:`float`
            The threshold that was exceeded.

        value: :obj:`float`
            The percentage by which the threshold was exceeded
        
        """
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
        """:obj:`str` : The string representation of the result.

        """
        rv = str()
        if self.index:
            t = self.domain.time[self.index]
            rv += f"id: {self.id}\n"
            rv += f"time: {t:.2f}{self.units.time}\n"
            rv += f"value: {self.value:.2f}%\n\n"
        else:
            rv += "None\n\n"
        return rv
    
    @property
    def header(self):
        """:obj:`list` [:obj:`str`] : The list of headers for a csv output.

        """
        return [
            "id",
            f"time ({self.units.time})",
            f"value (%)"
        ]

    @property
    def row(self):
        """:obj:`list` [:obj:`float`] : The list of values for a csv output.

        """
        if self.index:
            t = self.domain.time[self.index]
            return [self.id, t, self.value]
        else:
            return [self.id, "None", "None"]

    @property
    def fname(self):
        """:obj:`str` : the file name for the this result output.

        """
        return f"{self.geometry}_max%_exceeds_{self.threshold}{self.unit}.csv"

    @property
    def title(self):
        """:obj:`str` : the title string for this result.

        """
        return "Maximum % Threshold Exceedance"
    
    @property
    def extreme_title(self):
        """:obj:`str` : the extremum version of the title for this result.

        """
        return f"Maximum percentage exceeding {self.threshold}{self.unit} "\
               f"for {self.geometry}:"

    @property
    def valid(self):
        """:obj:`bool` : Returns true if contains valid index, else false.

        """
        return True if self.index else False
