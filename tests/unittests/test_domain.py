import unittest
import json

import numpy as np

from config import IDMFConfig

from container import Domain


class TestDomain(unittest.TestCase):

    """Unit tests for the :class:`~.Domain` class."""

    def setUp(self) -> None:

        """setUp method which instantiates the :class:`~.IDMFConfig` class,
        and the :class:`~.Domain` class."""

        with open("default/config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)
        self.domain = Domain(self.config)

    def test_point(self):

        """Tests to make sure that the types of the points
        are arrays."""

        points = self.config.models.eddy_diffusion.monitor_locations.points
        for point in points.values():
            for array in self.domain.points(point):
                self.assertEqual(type(array), np.ndarray)

    def test_line(self):

        """Tests to make sure that the types of the lines
        are arrays."""

        lines = self.config.models.eddy_diffusion.monitor_locations.lines
        for line in lines.values():
            for array in self.domain.lines(line):
                self.assertEqual(type(array), np.ndarray)

    def test_plane(self):

        """Tests to make sure that the types of the planes
        are arrays."""

        planes = self.config.models.eddy_diffusion.monitor_locations.planes
        for plane in planes.values():
            for array in self.domain.planes(plane):
                self.assertEqual(type(array), np.ndarray)
