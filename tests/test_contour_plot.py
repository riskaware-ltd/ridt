import unittest
import json
import os

import numpy as np
from matplotlib.contour import QuadContourSet

from config import IDMFConfig
from plot import ContourPlot


class TestContourPlot(unittest.TestCase):

    "Unit tests for the :class:`~.ContourPlot` class."""

    def setUp(self) -> None:

        """setUp method which instantiates the :class:`~.IDMFConfig` class,
        the :class:`~.ContourPlot` class, and creates some initial
        variables."""

        with open("tests/test_resources/test_config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)

        self.cp = ContourPlot(self.config, "tests/test_resources")

        self.time_array = np.linspace(0, 10, 10)
        self.x_array = np.linspace(0, 10, 10)
        self.conc, _ = np.meshgrid(self.x_array, self.x_array)
        self.planes = self.config.models.eddy_diffusion.monitor_locations.planes

    def tearDown(self) -> None:

        """tearDown method which removes and changes made in the
        tests."""

        resource_list = os.listdir("tests/test_resources")
        for file in resource_list:
            if file.endswith(".pdf"):
                os.remove(f"tests/test_resources/{file}")

    def test_plot(self):

        """tests the plots to make sure that is plot is
        of type :class:`~.QuadContourSet.`"""

        for plane in self.planes.values():
            plot = self.cp.plot(self.conc, plane)
            self.assertEqual(type(plot), QuadContourSet)

    def test_make_title(self):

        """tests to make sure that the title
        is of type :obj:`str`."""

        for plane in self.planes.values():
            title = self.cp.make_title(plane)
            self.assertEqual(type(title), str)


if __name__ == "__main__":
    unittest.main()
