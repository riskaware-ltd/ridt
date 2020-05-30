from typing import Tuple

from numpy import ndarray
from numpy import argmax
from numpy import unravel_index
from numpy import where
from numpy import prod

from ridt.base import Error
from ridt.base import ComputationalSpace

from ridt.config import RIDTConfig

FIRST = 0


class DataStore:

    class Dimensions:
        points = 1
        lines = 2
        planes = 3
        domain = 4

    def __init__(self):
        self.points = dict()
        self.lines = dict()
        self.planes = dict()
        self.domain = dict()
    
    def add(self, geometry: str, id: str, data: ndarray):
        try:
            self.verify(data, getattr(DataStore.Dimensions, geometry))
            getattr(self, geometry)[id] = data
        except AttributeError:
            raise DataStoreGeometryError(geometry)
    
    def get(self, geometry: str, id: str):
        try:
            return getattr(self, geometry)[id]
        except AttributeError:
            raise DataStoreGeometryError(geometry)
        except KeyError:
            raise DataStoreIDError(id, geometry)

    def verify(self, data: ndarray, dimensions: int):
        if not isinstance(data, ndarray):
            raise DataStoreTypeError(type(data))
        if len(data.shape) is not dimensions:
            raise DataStoreDimensionalityError(len(data.shape), dimensions)
    
    def maximum(self, geometry: str, id: str) -> Tuple[Tuple[int], ndarray]:
        data = self.get(geometry, id)
        index = unravel_index(argmax(data), data.shape)
        return index, data[index]
    
    def exceeds(self, geometry: str, id: str, value: float) -> Tuple[int]:
        data = self.get(geometry, id)
        exceeds = self.zip(where(data >= value))
        return exceeds[FIRST] if exceeds else None

    def percentage_exceeds(self, geometry: str, id: str, value: float, percent: float) -> int:
        data = self.get(geometry, id)
        shape = data.shape
        try:
            size = prod(shape[1:])
        except KeyError:
            size = 1
        for time in range(shape[0]):
            frac = 100 * len(self.zip(where(data[time] >= value))) / size
            if frac >= percent:
                return time
        return None
    
    def percentage_exceeds_max(self, geometry: str, id: str, value: float) -> Tuple[int, float]:
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

