import json

from typing import Type

from config.idmfconfig import IDMFConfig
from base.exceptions import Error
from base.settings import SettingErrorMessage


class ConfigFileWriter:
    """The class which handles the configuration file writing.

    This class handles the writing of configuration files from disk, as well as
    the instantiation of the :class:`~.IDMFConfig` instances using the written
    data.

    Attributes
    ----------
    path : :obj:`str`
        The path to the file in which to write the configuration JSON.
    
    data : :obj:`dict`
        The configuration stored as a :obj:`dict`.

    """

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, path: str, data: dict):
        """The way that the functionality of the :class:`~.ConfigFileWriter`
        class is accessed.

        Parameters
        ----------
        path : :obj:`str`
            The path to the file where the configuration will be written.

        data : :obj:`dict`
            The data to be written.

        Returns
        -------
        :class:`~.IDMFConfig`
            The :class:`~.IDMFConfig` instances created with the data written
            from `path`.

        """
        self.path = path
        self.data = data
        self.__write_file()
        
    def __write_file(self):
        """The method which writes the configuration file.

        Returns
        -------
        None

        Raises
        ------
        :class:`~.ConfigFileWriterJSONError`
            If the structure of the written JSON is invalid.
        
        :class:`~.ConfigFileWriterOSError`
            If an :obj:`OSError` is raised when writing the file.

        """

        try:
            with open(self.path, 'w') as f:
                 f.write(json.dumps(self.data, indent=4))
        except OSError as e:
            raise ConfigFileWriterOSError(self.path, e)

class ConfigFileWriterOSError(Error):
    """The exception raised when a :class:`~.ConfigFileWriter` instance
    catches an error when writing a config file path, or instantiating the
    :class:`~.Settings` derived class.

    """
    def __init__(self, path: str, error: OSError):
        """The constructor for the :class:`ConfigFileWriterOSError` class.

        """
        msg = f"While loading {path}, I encountered the following error:"\
              f"\n {error}"
        super().__init__(msg)
