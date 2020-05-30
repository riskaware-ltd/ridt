import unittest
import json
import os

import numpy as np
from matplotlib.contour import QuadContourSet

from ridt.config import RIDTConfig
from ridt.plot import ContourPlot


class TestContourPlot(unittest.TestCase):

    "Unit tests for the :class:`~.ContourPlot` class."""

    def setUp(self) -> None:

        """setUp method which instantiates the :class:`~.RIDTConfig` class,
        the :class:`~.ContourPlot` class, and creates some initial
        variables."""

        with open("tests/unittests/test_resources/test_config.json") as f:
            loaded_json = json.load(f)

        self.config = RIDTConfig(loaded_json)

        self.cp = ContourPlot(self.config, "tests/unittests/test_resources", "concentration")

        self.time_array = np.linspace(0, 10, 10)
        self.x_array = np.linspace(0, 10, 10)
        self.conc, _ = np.meshgrid(self.x_array, self.x_array)
        self.planes = self.config.models.eddy_diffusion.monitor_locations.planes

    def tearDown(self) -> None:

        """tearDown method which removes and changes made in the
        tests."""

        resource_list = os.listdir("tests/unittests/test_resources")
        for file in resource_list:
            if file.endswith(".pdf"):
                os.remove(f"tests/unittests/test_resources/{file}")

if __name__ == "__main__":
    unittest.main()
