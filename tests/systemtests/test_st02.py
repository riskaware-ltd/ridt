import unittest

from config import ConfigFileParser
from config import ConsistencyError


class ST02(unittest.TestCase):

    """System Test 02. The objective is to able to parse monitor
       points/lines/planes parallel to the principle axes from the JSON file,
       to be evaluated by the Eddy Diffusion model."""

    def setUp(self) -> None:

        """setUp method which instantiates an
        :class:`~.IDMFConfig` class."""

        with ConfigFileParser("default/config.json") as cfp:
            self.c = cfp

    def test_verify(self):

        """"Verifies that the :class:`~.IDMFConfig` class contains the
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

    def test_lines(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the line does not lie in the bounds of the container
        or is not parallel to one of the principle axes."""

        ed = self.c.models.eddy_diffusion
        lines = ed.monitor_locations.lines
        for line in lines.values():
            axis = getattr(line, "parallel_axis")
            with self.assertRaises(ConsistencyError):
                setattr(line.point, axis, getattr(ed.dimensions, axis) + 1)
                self.c.consistency_check()
            setattr(line.point, axis, getattr(ed.dimensions, axis) - 1)

    def test_points(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the point does not lie in the bounds of the container."""

        ed = self.c.models.eddy_diffusion
        points = ed.monitor_locations.points
        dims = ["x", "y", "z"]
        for point in points.values():
            for dim in dims:
                setattr(point, dim, getattr(ed.dimensions, dim) + 1)
                with self.assertRaises(ConsistencyError):
                    self.c.consistency_check()
                setattr(point, dim, getattr(ed.dimensions, dim) - 1)

    def test_planes(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if a plane lies outside of the bounds of the container."""

        ed = self.c.models.eddy_diffusion
        for key, val in ed.monitor_locations.planes.items():
            if val.axis == "xy":
                val.distance = ed.dimensions.z + 1
                self.assertRaises(ConsistencyError, self.c.consistency_check)
            if val.axis == "xz":
                val.distance = ed.dimensions.y + 1
                self.assertRaises(ConsistencyError, self.c.consistency_check)
            if val.axis == "zy":
                val.distance = ed.dimensions.x + 1
                self.assertRaises(ConsistencyError, self.c.consistency_check)
            val.axis = "RANDOM VALUE"
            self.assertRaises(ConsistencyError, self.c.consistency_check)


if __name__ == "__main__":
    unittest.main()
