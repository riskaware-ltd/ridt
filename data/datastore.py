from numpy import ndarray

from base.settings import ComputationalSpace
from config.idmfconfig import IDMFConfig
from base.exceptions import Error


class DataStore:

    def __init__(self):
        self.points = dict()
        self.lines = dict()
        self.planes = dict()
        self.domain = dict()
    
    def add_point_data(self, setting: IDMFConfig, id_str: str, data: ndarray):
        self.verify(data, 1)
        if setting not in self.points:
            self.points[setting] = dict()
        else:
            self.points[setting][id_str] = data

    def add_line_data(self, setting: IDMFConfig, id_str: str, data: ndarray):
        self.verify(data, 2)
        if setting not in self.lines:
            self.lines[setting] = dict()
        else:
            self.lines[setting][id_str] = data

    def add_plane_data(self, setting: IDMFConfig, id_str: str, data: ndarray):
        self.verify(data, 3)
        if setting not in self.planes:
            self.planes[setting] = dict()
        else:
            self.planes[setting][id_str] = data
    
    def add_domain_data(self, setting: IDMFConfig, data: ndarray):
        self.verify(data, 4)
        self.domain[setting] = data
    
    def get_point_data(self, setting: IDMFConfig, id_str: str) -> ndarray:
        try:
            return self.points[setting][id_str]
        except KeyError as e:
            raise DataStoreIDError(setting, id_str, "point")
    
    def get_line_data(self, setting: IDMFConfig, id_str: str) -> ndarray:
        try:
            return self.lines[setting][id_str]
        except KeyError as e:
            raise DataStoreIDError(setting, id_str, "line")
    
    def get_plane_data(self, setting: IDMFConfig, id_str: str) -> ndarray:
        try:
            return self.planes[setting][id_str]
        except KeyError as e:
            raise DataStoreIDError(setting, id_str, "plane")
    
    def get_domain_data(self, setting: IDMFConfig):
        if self.domain:
            return self.domain
        else:
            raise DataStoreIDError(setting, "", "domain")

    def verify(self, data: ndarray, dimensions: int):
        if not isinstance(data, ndarray):
            raise DataStoreTypeError(type(data))
        if len(data.shape) is not dimensions:
            raise DataStoreDimensionalityError(len(data.shape), dimensions)



class DataStoreIDError(Error):
    """The exception raised when the data store is queries with an id string
    it does not recognise.

    """
    def __init__(self, setting: IDMFConfig, id_str: str, kind: str):
        """The constructor for the :class:`DataStoreIDError` class.

        """
        if id_str:
            msg = f"The data store does not contain any {kind} data with ID "\
                  f"{id_str} for setting object {setting}"
        else:
            msg = f"The data store does not contain any {kind} data for "\
                  f"settings object {setting}."
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



