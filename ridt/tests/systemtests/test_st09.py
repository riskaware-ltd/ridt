import unittest

import os

import json

from ridt.config import ConfigFileParser
from ridt.config.ridtconfig import ConsistencyError

from ridt.config.configfileparser import ConfigFileParserValidationError


class ST11(unittest.TestCase):

    """System Test 11. Test the system can convert
       config files with ranges of values into a set of
       config object, each which can be evaluated separately."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.RIDTConfig` class."""

        this_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(this_dir, "st06/config.json")
        with open(self.config_path) as f:
            self.default = json.load(f)

        this_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(this_dir, "../../default/config.json")
        with ConfigFileParser(path) as cfp:
            self.c = cfp

    def tearDown(self) -> None:

        with open(self.config_path, "w") as w:
            json.dump(self.default, w)

    def test_verify(self):

        """Verify that the :class:`~.ContourPlots` class
        has the correct scale and range attributes."""

        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.planes_plots, "range"), True
        )
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.planes_plots, "scale"), True
        )

    def test_contours(self):

        with self.assertRaises(ConfigFileParserValidationError):
            with open(self.config_path) as f:
                config = json.load(f)
            config["models"]["eddy_diffusion"]["planes_plots"]["contours"]["min"] = \
                config["models"]["eddy_diffusion"]["planes_plots"]["contours"]["max"] + 1
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            ConfigFileParser(self.config_path)

    def test_range(self):

        with self.assertRaises(ConfigFileParserValidationError):
            with open(self.config_path) as f:
                config = json.load(f)
            config["models"]["eddy_diffusion"]["planes_plots"]["range"] = "test"
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            ConfigFileParser(self.config_path)

    def test_scale(self):

        with self.assertRaises(ConfigFileParserValidationError):
            with open(self.config_path) as f:
                config = json.load(f)
            config["models"]["eddy_diffusion"]["planes_plots"]["scale"] = "test"
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            ConfigFileParser(self.config_path)


if __name__ == "__main__":
    unittest.main()
