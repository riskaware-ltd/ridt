import json

from os.path import join

from typing import Type

from ridt.base import Error
from ridt.base import SettingErrorMessage

from ridt.config import RIDTConfig


class ConfigFileWriter:
    """The class which handles the configuration file writing.

    This class handles the writing of configuration files from disk, as well as
    the instantiation of the :class:`~.RIDTConfig` instances using the written
    data.

    Attributes
    ----------
    path : :obj:`str`
        The path to the file in which to write the configuration JSON.
    
    data : :obj:`dict`
        The configuration stored as a :obj:`dict`.

    """
    def __new__(cls, *args, **kwargs):
        instance = super(ConfigFileWriter, cls).__new__(cls)
        instance.__init__(*args, **kwargs)

    def __init__(self, output_dir: str, file_name: str, data: dict):
        self.path = join(self.output_dir, file_name)
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
