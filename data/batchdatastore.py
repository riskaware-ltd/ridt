from config.idmfconfig import IDMFConfig
from data.datastore import DataStore


class BatchDataStore:

    def __init__(self):
        self.store = dict()

    def add_run(self, setting: IDMFConfig):
        if setting not in self.store:
            self.store[setting] = DataStore()
        else:
            pass

    def get_run(self, setting: IDMFConfig) -> DataStore:
        try:
            return self.store[setting]
        except KeyError as e:
            raise BatchDataStoreIDError(setting)


class BatchDataStoreIDError(Error):
    """The exception raised when the data store is queries with settings object 
    it does not recognise.

    """
    def __init__(self, setting: IDMFConfig):
        """The constructor for the :class:`BatchDataStoreIDError` class.

        """
        msg = f"The data store does not contain any data for "\
                f"settings object {setting}."
        super().__init__(msg)

