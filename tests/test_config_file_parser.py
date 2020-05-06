import unittest

from config import IDMFConfig
from config.configfileparser import ConfigFileParser
from config.configfileparser import ConfigFileParserOSError
from config.configfileparser import ConfigFileParserJSONError
from config.configfileparser import ConfigFileParserValidationError


class TestConfigFileParser(unittest.TestCase):

    def setUp(self) -> None:
        self.idmf = IDMFConfig
        self.cfp = ConfigFileParser()

    def test_parse_file(self):

        with self.assertRaises(ConfigFileParserOSError):
            self.cfp("random_path")

        with self.assertRaises(ConfigFileParserJSONError):
            self.cfp("test_resources/decode_error_config.json")

    def test_instantiate_settings(self):

        with self.assertRaises(ConfigFileParserValidationError):
            self.cfp("test_resources/missing_input_config.json")


if __name__ == "__main__":
    unittest.main()
