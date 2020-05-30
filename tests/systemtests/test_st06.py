import unittest
import json

from config import ConfigFileParser
from config.ridtconfig import ConsistencyError
from config.configfileparser import ConfigFileParserValidationError


class ST06(unittest.TestCase):

    """System Test 06. Test that the system can parse
     all physical unit specifications from the JSON file."""

    def setUp(self) -> None:

        """setUp method that instantiates the
        :class:`~.RIDTConfig` class."""

        self.config_path = "tests/systemtests/st06/config.json"
        with open(self.config_path) as f:
            self.default = json.load(f)

        with ConfigFileParser("default/config.json") as cfp:
            self.c = cfp

    def tearDown(self) -> None:

        with open(self.config_path, "w") as w:
            json.dump(self.default, w)

    def test_verify(self):

        """Verifies that the :class:`~.RIDTConfig` class
        contains the correct the attributes."""

        self.assertEqual(
            hasattr(self.c, "time_units"), True)
        self.assertEqual(
            hasattr(self.c, "concentration_units"), True)
        self.assertEqual(
            hasattr(self.c, "exposure_units"), True)

    def test_concentration_units(self):

        with self.assertRaises(ConfigFileParserValidationError):
            with open(self.config_path) as f:
                config = json.load(f)
            config["concentration_units"] = "test"
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            ConfigFileParser(self.config_path)

    def test_spatial_units(self):

        with self.assertRaises(ConfigFileParserValidationError):
            with open(self.config_path) as f:
                config = json.load(f)
            config["spatial_units"] = "test"
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            ConfigFileParser(self.config_path)

    def test_exposure_units(self):

        with self.assertRaises(ConfigFileParserValidationError):
            with open(self.config_path) as f:
                config = json.load(f)
            config["exposure_units"] = "test"
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            ConfigFileParser(self.config_path)

    def test_mass_units(self):
        with self.assertRaises(ConfigFileParserValidationError):
            with open(self.config_path) as f:
                config = json.load(f)
            config["mass_units"] = "test"
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            ConfigFileParser(self.config_path)

    def test_time_units(self):
        with self.assertRaises(ConfigFileParserValidationError):
            with open(self.config_path) as f:
                config = json.load(f)
            config["time_units"] = "test"
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            ConfigFileParser(self.config_path)


if __name__ == "__main__":
    unittest.main()
