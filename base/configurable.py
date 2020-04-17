import sys
import json

from base.settings import Settings
from base.exceptions import Error


class Configurable:
    """A base class for classes which have a
    :class:`~.Settings` derived class.

    It simply parses a json file and passes the resultant :obj:`dict` to the
    constructor of a :class:`~.Settings` derived class. The resultant
    :class:`~.Settings` derived instance is available to the parent class by way
    of the `settings` property.

    """
    def __init__(self, settings_class: Settings, config_file_path: str):
        """The constructor for the :class:`~.Configurable` class is defined as
        follows:

        Parameters
        ----------
        settings_class : :class:`~.Settings`
            A :class:`~.Settings` derived class. Note this should not be an
            instance, but the actual class.

        config_file_path : :obj:`str`
            The path to the json file containing the settings file
            configuration.

        Raises
        ------
        :exc:`ConfigFileLoadError`
            Raised if the configuration file could not be opened at the given
            location.

        :exc:`ConfigFileParseError`
            Raised if the json in the configuration file could not be parsed.

        """
        try:
            with open(config_file_path, 'r') as f:
                self._settings = settings_class(json.loads(f.read()))
        except (OSError, IOError):
            raise ConfigFileLoadError(self.__class__.__name__,
                                      config_file_path)
        except json.JSONDecodeError:
            raise ConfigFileParseError(self.__class__.__name__,
                                       config_file_path)

    @property
    def settings(self):
        """:class:`~.Settings`: The instance of
        :class:`~.Settings`.

        """
        return self._settings


class ConfigFileLoadError(Error):
    """The exception class raised when the config file cannot be opened.

    """
    def __init__(self, class_name: str, config_file_path: str):
        """The constructor for the :class:`ConfigFileLoadError` exception.

        Parameters
        ----------
        class_name : :obj:`str`
            The name of the class for which the settings are being loaded.

        config_file_path : :obj:`str`
            The path to the configuration file being loaded.

        """
        msg = f"Could not open the {class_name} config file, from " \
              f"the path {config_file_path}"
        super().__init__(msg)


class ConfigFileParseError(Error):
    """The exception class raised when the json in the config file cannot be
    parsed.

    """
    def __init__(self, class_name: str, config_file_path: str):
        """The constructor for the :class:`ConfigFileParseError` exception.

        Parameters
        ----------
        class_name : :obj:`str`
            The name of the class for which the settings are being loaded.

        config_file_path : :obj:`str`
            The path to the configuration file being loaded.

        """
        msg = f"Could not parse the json in the {class_name} config file, " \
              f"located at {config_file_path}."
        super().__init__(msg)
