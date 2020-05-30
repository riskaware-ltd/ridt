import json

from typing import Type

from base import Error
from base import SettingErrorMessage

from config import RIDTConfig


class ConfigFileParser:
    """The class which handles the configuration file parsing.

    This class handles the parsing of configuration files from disk, as well as
    the instantiation of the :class:`~.RIDTConfig` instances using the parsed
    data.

    Attributes
    ----------
    path : :obj:`str`
        The path to the file containing the configuration JSON.
    
    data : :obj:`dict`
        The parsed JSON, stored as a :obj:`dict`.

    """
    def __new__(cls, *args, **kwargs):
        instance = super(ConfigFileParser, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.settings

    def __init__(self, path: str):
        self.path = path
        self.__parse_file()
        self.settings = self.__instantiate_settings()

    def __parse_file(self):
        """The method which parses the configuration file.

        Returns
        -------
        None

        Raises
        ------
        :class:`~.ConfigFileParserJSONError`
            If the structure of the parsed JSON is invalid.
        
        :class:`~.ConfigFileParserOSError`
            If an :obj:`OSError` is raised when parsing the file.

        """

        try:
            with open(self.path, 'r') as f:
                self.data = json.loads(f.read())
        except json.JSONDecodeError as e:
            raise ConfigFileParserJSONError(self.path, e)
        except OSError as e:
            raise ConfigFileParserOSError(self.path, e)

    def __instantiate_settings(self):
        """The method which instantiates the :class:`~.RIDTConfig` instances
        using the parsed data.

        Returns
        -------
        :class:`~.RIDTConfig`
            The :class:`~.RIDTConfig` instance created using the parsed data.
        
        Raises
        ------
        :class:`~.ConfigFileParserValidationError`
            If any :class:`~.SettingErrorMessage` errors are raised when
            instantiating the :class:`~.RIDTConfig` class.

        """
        try:
            return RIDTConfig(self.data)
        except SettingErrorMessage as e:
            raise ConfigFileParserValidationError(self.path, e)

class ConfigFileParserOSError(Error):
    """The exception raised when a :class:`~.ConfigFileParser` instance
    catches an error when parsing a config file path, or instantiating the
    :class:`~.Settings` derived class.

    """
    def __init__(self, path: str, error: OSError):
        """The constructor for the :class:`ConfigFileParserOSError` class.

        """
        msg = f"While loading {path}, I encountered the following error:"\
              f"\n {error}"
        super().__init__(msg)

class ConfigFileParserJSONError(Error):
    """The exception raised when a :class:`~.ConfigFileParser` instance
    catches an error when parsing a the JSON in a string parsed from a file.

    """
    def __init__(self, path: str, error: json.JSONDecodeError):
        """The constructor for the :class:`ConfigFileParserJSONError` class.

        """
        msg = f"While loading {path}, I encountered the following error:"\
              f"\n {error}. Please verify the integrity of the JSON file."
        super().__init__(msg)

class ConfigFileParserValidationError(Error):
    """The exception raised when a :class:`~.ConfigFileParser` instance
    catches an error when parsing a the JSON in a string parsed from a file.

    """
    def __init__(self, path: str, error: SettingErrorMessage):
        """The constructor for the :class:`ConfigFileParserValidationError`
        class.

        """
        msg = f"While loading {path}, I encountered the following error:"\
              f"\n {error}."
        super().__init__(msg)

