import json

from typing import Type

from config.idmfconfig import IDMFConfig
from base.exceptions import Error
from base.settings import SettingErrorMessage


class ConfigFileParser:

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, path: str):
        self.__parse_file(path)
        return self.__instantiate_settings()
        
    def __parse_file(self, path: str):
        self.path = path

        try:
            with open(self.path, 'r') as f:
                self.data = json.loads(f.read())
        except json.JSONDecodeError as e:
            raise ConfigFileParserError(self.path, e)
        except OSError as e:
            raise ConfigFileParserError(self.path, e)

    def __instantiate_settings(self):
        try:
            return IDMFConfig(self.data)
        except SettingErrorMessage as e:
            raise ConfigFileParserError(self.path, e)

class ConfigFileParserError(Error):
    """The exception raised when a :class:`~.ConfigFileParser` instance
    catches an error when parsing a config file path, or instantiating the
    :class:`~.Settings` derived class.

    """
    def __init__(self, path: str, error: Type[Exception]):
        """The constructor for the :class:`ConfigFileParserError` class.

        """
        msg = f"While loading {path}, I encountered the following error:"\
              f"\n {error}"
        super().__init__(msg)

