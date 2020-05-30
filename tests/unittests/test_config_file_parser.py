import unittest

from config import RIDTConfig
from config.configfileparser import ConfigFileParser
from config.configfileparser import ConfigFileParserOSError
from config.configfileparser import ConfigFileParserJSONError
from config.configfileparser import ConfigFileParserValidationError


class TestConfigFileParser(unittest.TestCase):

    """The unit tests for the :class:`~.ConfigFileParser` class."""

    def setUp(self) -> None:

        """setUp method which instantiates the :class:`~.RIDTConfig` class,
        and the :class:`~.ConfigFileParser` class."""

        self.ridt = RIDTConfig

    def test_parse_file(self):

        """Checks if the :class:`~.ConfigFileParserOSError` error
        is passed when the path is unknown.
        Checks to see if the :class:`~.ConfigFileParserJSONError` error
        is passed when there isa decode error in the json file."""

        with self.assertRaises(ConfigFileParserOSError):
            ConfigFileParser("random_path")

        with self.assertRaises(ConfigFileParserJSONError):
            ConfigFileParser("tests/unittests/test_resources/decode_error_config.json")

    def test_instantiate_settings(self):

        """"Checks to make sure that the :class:`~.ConfigFileParserValidationError`
        error passes when there is a missing input within the config file."""

        with self.assertRaises(ConfigFileParserValidationError):
            ConfigFileParser("tests/unittests/test_resources/missing_input_config.json")


if __name__ == "__main__":
    unittest.main()
