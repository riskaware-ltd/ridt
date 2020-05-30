import unittest

import json

from ridt.config import ConfigFileParser
from ridt.config.ridtconfig import ConsistencyError
from ridt.config.configfileparser import ConfigFileParserValidationError


class ST02(unittest.TestCase):

    """System Test 02. The objective is to able to parse monitor
       points/lines/planes parallel to the principle axes from the JSON file,
       to be evaluated by the Eddy Diffusion model."""

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

        """"Verifies that the :class:`~.RIDTConfig` class contains the
        monitor locations attributes."""

        self.assertEqual(
            hasattr(self.c, "models"), True)
        self.assertEqual(
            hasattr(self.c.models, "eddy_diffusion"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion, "monitor_locations"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.monitor_locations, "points"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.monitor_locations, "lines"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.monitor_locations, "planes"), True)

    def test_verify_points(self):

        """Verifies that the :class:`~.Point` class contains the
        correct attributes."""

        for point in self.c.models.eddy_diffusion.monitor_locations.points.values():
            self.assertEqual(hasattr(point, "x"), True)
            self.assertEqual(hasattr(point, "y"), True)
            self.assertEqual(hasattr(point, "z"), True)

    def test_verify_lines(self):

        """Verifies that the :class:`~.Line` class contains the
        correct attributes."""

        for line in self.c.models.eddy_diffusion.monitor_locations.lines.values():
            self.assertEqual(hasattr(line, "point"), True)
            self.assertEqual(hasattr(line.point, "x"), True)
            self.assertEqual(hasattr(line.point, "y"), True)
            self.assertEqual(hasattr(line.point, "z"), True)
            self.assertEqual(hasattr(line, "parallel_axis"), True)

    def test_verify_planes(self):

        """Verifies that the :class:`~.Plane` class contains the
        correct attributes."""

        for plane in self.c.models.eddy_diffusion.monitor_locations.planes.values():
            self.assertEqual(hasattr(plane, "axis"), True)
            self.assertEqual(hasattr(plane, "distance"), True)

    def test_line_dims(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the line does not lie in the bounds of the container
        or is not parallel to one of the principle axes."""

        with self.assertRaises(ConsistencyError):
            with open(self.config_path) as f:
                config = json.load(f)
            for lines in config["models"]["eddy_diffusion"]["monitor_locations"]["lines"].values():
                lines["point"]["x"] = config["dimensions"]["x"] + 1
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            ConfigFileParser(self.config_path)

    def test_line_axis(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the line does not lie in the bounds of the container
        or is not parallel to one of the principle axes."""

        with self.assertRaises(ConfigFileParserValidationError):
            with open(self.config_path) as f:
                config = json.load(f)
            for lines in config["models"]["eddy_diffusion"]["monitor_locations"]["lines"].values():
                lines["parallel_axis"] = "test"
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            ConfigFileParser(self.config_path)

    def test_points(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the point does not lie in the bounds of the container."""

        with self.assertRaises(ConsistencyError):
            with open(self.config_path) as f:
                config = json.load(f)
            for points in config["models"]["eddy_diffusion"]["monitor_locations"]["points"].values():
                points["x"] = config["dimensions"]["x"] + 1
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            ConfigFileParser(self.config_path)

    def test_planes_axis(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if a plane lies outside of the bounds of the container."""

        with self.assertRaises(ConfigFileParserValidationError):
            with open(self.config_path) as f:
                config = json.load(f)
            for planes in config["models"]["eddy_diffusion"]["monitor_locations"]["planes"].values():
                planes["axis"] = "test"
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            ConfigFileParser(self.config_path)

    def test_planes_distance(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if a plane lies outside of the bounds of the container."""

        with self.assertRaises(ConsistencyError):
            with open(self.config_path) as f:
                config = json.load(f)
            for planes in config["models"]["eddy_diffusion"]["monitor_locations"]["planes"].values():
                axis = [x for x in ["x", "y", "z"] if x not in list(planes["axis"])]
                planes["distance"] = config["dimensions"][axis[0]] + 1
            with open(self.config_path, "w") as f:
                json.dump(config, f)
            ConfigFileParser(self.config_path)


if __name__ == "__main__":
    unittest.main()
