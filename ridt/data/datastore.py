from typing import Tuple

from numpy import ndarray
from numpy import nanargmax
from numpy import unravel_index
from numpy import where
from numpy import prod
from numpy import isnan
from numpy import count_nonzero

from ridt.base import Error


class DataStore:
    """The data store than contains computed quantities over various geometries.

    There are four different sub stores for point, line, plane and full domain 
    grids. They can store quantities corresponding to different monitor
    locations defined in a settings file. The store data for various times (axis
    0) It also provides calculation of various quantities over the various
       grids.

    Attributes
    ----------
    points : :obj:`Dict`[:obj:`str`, :class:`~numpy.ndarray`]
        The dictionary containing all point monitor location value grids.

    lines : :obj:`Dict`[:obj:`str`, :class:`~numpy.ndarray`]
        The dictionary containing all line monitor location value grids.

    planes : :obj:`Dict`[:obj:`str`, :class:`~numpy.ndarray`]
        The dictionary containing all plane monitor location value grids.

    domain : :obj:`Dict`[:obj:`str`, :class:`~numpy.ndarray`]
        The dictionary containing all full domain value grids.

    """
    class Dimensions:
        """A 'static' member class that contains information about the

        dimensionality of the different geometry types.

        """
        points = 1
        lines = 2
        planes = 3
        domain = 4

    def __init__(self):
        """The :class:`DataStore` constructor.

        """
        self.points = dict()
        self.lines = dict()
        self.planes = dict()
        self.domain = dict()
    
    def add(self, geometry: str, id: str, data: ndarray)-> None:
        """Adds a new item to the data store.

        Parameters
        ----------
        geometry : :obj:`str`
            The type of grid to be stored.

        id : :obj:`str`
            The id of the grid to be stored.

        data : :class:`~ndarray.ndarray`
            The grid to be stored.

        Raises
        ------
        :class:`~.DataStoreGeometryError`
            If the passed geometry type is invalid.

        Returns
        -------
        None

        """
        try:
            self.verify(data, getattr(DataStore.Dimensions, geometry))
            getattr(self, geometry)[id] = data
        except AttributeError:
            raise DataStoreGeometryError(geometry)
    
    def get(self, geometry: str, id: str) -> ndarray:
        """Returns the grid given a geometry type and id string.

        Parameters
        ----------
        geometry : :obj:`str`
            The type of grid to be found.

        id : :obj:`str`
            The id of the grid to be found.

        Returns
        -------
        :class:`~numpy.ndarray`
            The grid to be stored.

        Raises
        ------
        :class:`~.DataStoreGeometryError`
            If the passed geometry type is invalid.
        :class:`~.DataStoreIDError`
            If the passed ID does not exist in the store..

        """
        try:
            return getattr(self, geometry)[id]
        except AttributeError:
            raise DataStoreGeometryError(geometry)
        except KeyError:
            raise DataStoreIDError(id, geometry)

    def verify(self, data: ndarray, dimensions: int) -> None:
        """Verifies if a grid is valid.

        Parameters
        ----------
        data : :class:`~ndarray.ndarray`
            The grid to be verified.

        dimensions : :obj:`int`
            The number of dimensions the grid should have.

        Raises
        ------
        :class:`~.DataStoreTypeError`
            If the grid is not a numpy array.

        :class:`~.DataStoreDimensionalityError`
            If the grid has the incorrect number of dimensions.
        """
        if not isinstance(data, ndarray):
            raise DataStoreTypeError(type(data))
        if len(data.shape) is not dimensions:
            raise DataStoreDimensionalityError(len(data.shape), dimensions)
    
    def maximum(self, geometry: str, id: str) -> Tuple[Tuple[int], ndarray]:
        """Finds and returns the maximum value, and its index, of a grid.

        Parameters
        ----------
        geometry : :obj:`str`
            The type of grid to be evaluated.

        id : :obj:`str`
            The id of the grid to be evaluated.

        Returns
        -------
        :obj:`Tuple`[:obj:`Tuple`[:obj:`int`], float]
            The index and value of the maximum in the grid.

        """
        data = self.get(geometry, id)
        try:
            index = unravel_index(nanargmax(data), data.shape)
        except ValueError:
            index = None
        return index, data[index]
    
    def exceeds(self, geometry: str, id: str, value: float) -> Tuple[int]:
        """Returns the index of the first time a grid exceeds 'value'

        Parameters
        ----------
        geometry : :obj:`str`
            The type of grid to be evaluated.

        id : :obj:`str`
            The id of the grid to be evaluated.

        value : :obj:`float`
            The threshold to be exceeded.

        Returns
        -------
        :obj:`Union`[:obj:`Tuple`[:obj:`int`], None]
            The index where and when the first exceedence occurred, or None if
            no exceedence.

        """
        data = self.get(geometry, id)
        exceeds = self.zip(where(data >= value))
        return exceeds[0] if exceeds else None

    def percentage_exceeds(self, geometry: str, id: str, value: float, percent: float) -> int:
        """Returns the time index where 'percent'% of the grid exceeds 'value'

        Parameters
        ----------
        geometry : :obj:`str`
            The type of grid to be evaluated.

        id : :obj:`str`
            The id of the grid to be evaluated.

        value : :obj:`float`
            The threshold to be exceeded.

        percent : :obj:`float`
            The percentage of the grid required to exceed 'value'.

        Returns
        -------
        :obj:`Union`[:obj:`int`, None]
            The time index where the percentage exceedence was reached or None
            if not reached during simulation.

        """
        data = self.get(geometry, id)
        for time in range(data.shape[0]):
            size = data[time].size - count_nonzero(isnan(data[time]))
            if not size:
                continue
            frac = 100 * len(self.zip(where(data[time] >= value))) / size
            if frac >= percent:
                return time
        return None
    
    def percentage_exceeds_max(self, geometry: str, id: str, value: float) -> Tuple[int, float]:
        """Returns the maximum percentage of grid that exceeds `value`.

        And the time index when it occurred.

        Parameters
        ----------
        geometry : :obj:`str`
            The type of grid to be evaluated.

        id : :obj:`str`
            The id of the grid to be evaluated.

        value : :obj:`float`
            The threshold to be exceeded.

        Returns
        -------
        :obj:`Tuple`[:obj:`Union`[:obj:`int`, None], :obj:`float`]
            The time index and the percentage exceedence, or None and zero if no
            exceedence.

        """
        data = self.get(geometry, id)
        max_val = 0.0
        max_time = None
        shape = data.shape
        try:
            size = prod(shape[1:])
        except KeyError:
            size = 1

        for time in range(shape[0]):
            frac = 100 * len(self.zip(where(data[time] >= value))) / size
            if frac > max_val:
                max_val = frac
                max_time = time
        return max_time, max_val
    
    def zip(self, where_output):
        return list(zip(*where_output))
 

class DataStoreIDError(Error):
    """The exception raised when the data store is queries with an id string
    it does not recognise.

    """
    def __init__(self, id_str: str, kind: str):
        """The constructor for the :class:`DataStoreIDError` class.

        """
        if id_str:
            msg = f"The data store does not contain any {kind} data with ID "\
                  f"{id_str}."
        else:
            msg = f"The data store does not contain any {kind} data."
        super().__init__(msg)


class DataStoreDimensionalityError(Error):
    """The exception raised when an array of the wrong shape is passed to the
    data store.

    """
    def __init__(self, dimensions: int, expected_dimensions: int):
        """The constructor for the :class:`DataStoreDimensionalityError` class.

        """
        msg = f"Expecting array with {expected_dimensions} dimensions, "\
              f"received array with {dimensions} dimensions."
        super().__init__(msg)


class DataStoreTypeError(Error):
    """The exception raised when anything other than a :class:`~numpy.ndarray`
    is passed to the data store.

    """
    def __init__(self, recieved_type: type):
        """The constructor for the :class:`DataStoreTypeError` class.

        """
        msg = f"Expecting {ndarray}, received {recieved_type}."
        super().__init__(msg)


class DataStoreGeometryError(Error):
    """The exception raised when the data store is queries with an geometry string
    it does not recognise.

    """
    def __init__(self, geometry_str: str):
        """The constructor for the :class:`DataStoreGeometryError` class.

        """
        msg = f"The  geometry '{geometry_str}' does not exist."
        super().__init__(msg)

