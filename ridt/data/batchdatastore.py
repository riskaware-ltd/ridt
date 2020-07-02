from typing import Dict

from ridt.base import Error

from ridt.config import RIDTConfig

from .datastore import DataStore


class BatchDataStore:
    """The data store than contains other data stores.

    This behaves like a dictionary with type restrictions, keys are
    :class:`~.RIDTConfig` instances and values are :class:`~.DataStore`
    instances. 

    Attributes
    ----------
    data_store : :obj:`Dict`[:class:`~.RIDTConfig`, :class:`~.DataStore`]
        The dictionary containing the data stores.

    """

    def __init__(self):
        """The :class:`BatchDataStore` constructor.

        """
        self.store = dict()

    def add_run(self, setting: RIDTConfig) -> None:
        """Add a new empty data store for a new settings instance.

        If settings instance already in :attr:`store`, does nothing.

        Parameters
        ----------
        setting : :class:`~.RIDTConfig`
            The settings for the run in question.
        
        Returns
        -------
        None

        """
        if setting not in self.store:
            self.store[setting] = DataStore()
        else:
            pass
    
    def values(self):
        """Interface for standard :obj:`dict` functionality.

        """
        return self.store.values()
    
    def keys(self):
        """Interface for standard :obj:`dict` functionality.

        """
        return self.store.keys()

    def items(self):
        """Interface for standard :obj:`dict` functionality.

        """
        return self.store.items()

    def __getitem__(self, setting: RIDTConfig) -> DataStore:
        """Interface for standard :obj:`dict` functionality, with type restrict.

        Raises
        ------
        :class:`BatchDataStoreIDError`
            If the requested settings instance is not in the store.

        """
        try:
            return self.store[setting]
        except KeyError as e:
            raise BatchDataStoreIDError(setting)

    def __setitem__(self, setting: RIDTConfig, value: DataStore):
        """Interface for standard :obj:`dict` functionality, with type restrict.

        Raises
        ------
        :class:`BatchDataStoreIDError`
            If the requested settings instance is not in the store.

        :class:`BatchDataStoreValueError`
            If `value` is not a :class:`~.DataStore` instance.

        """
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

