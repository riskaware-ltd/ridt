import unittest
import json
import os

import numpy as np

from ridt.config import RIDTConfig

from ridt.container import Domain


class TestDomain(unittest.TestCase):

    def setUp(self) -> None:

        this_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(this_dir, "../../default/config.json")
        with open(path) as f:
            loaded_json = json.load(f)

        self.config = RIDTConfig(loaded_json)
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
