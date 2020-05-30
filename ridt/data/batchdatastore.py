from ridt.base import Error

from ridt.config import RIDTConfig

from .datastore import DataStore


class BatchDataStore:

    def __init__(self):
        self.store = dict()

    def add_run(self, setting: RIDTConfig):
        if setting not in self.store:
            self.store[setting] = DataStore()
        else:
            print(setting)
            pass
    
    def values(self):
        return self.store.values()
    
    def keys(self):
        return self.store.keys()

    def items(self):
        return self.store.items()

    def __getitem__(self, setting: RIDTConfig) -> DataStore:
        try:
            return self.store[setting]
        except KeyError as e:
            raise BatchDataStoreIDError(setting)

    def __setitem__(self, setting: RIDTConfig, value: DataStore):
        if not isinstance(value, DataStore):
            raise BatchDataStoreValueError()
        try:
            self.store[setting] = value
        except KeyError as e:
            raise BatchDataStoreIDError(setting)


class BatchDataStoreIDError(Error):
    """The exception raised when the data store is queries with settings object 
    it does not recognise.

    """
    def __init__(self, setting: RIDTConfig):
        """The constructor for the :class:`BatchDataStoreIDError` class.

        """
        msg = f"The data store does not contain any data for "\
                f"settings object {setting}."
        super().__init__(msg)


class BatchDataStoreValueError(Error):
    """The exception raised when an instance of some class other than DataStore
    is passed to __setitem__ 

    """
    def __init__(self):
        """The constructor for the :class:`BatchDataStoreValueError` class.

        """
        msg = f"The data store can only hold {DataStore} instances."
        super().__init__(msg)

