import unittest
import json
import os

import numpy as np
from matplotlib.lines import Line2D

from config import RIDTConfig
from plot import PointPlot


class TestPointPlot(unittest.TestCase):

    "Unit tests for the :class:`~.PointPlot` class."""

    def setUp(self) -> None:

        """setUp method which instantiates the :class:`~.RIDTConfig` class,
        the :class:`~.PointPlot` class, and creates some initial
        variables."""

        with open("tests/unittests/test_resources/test_config.json") as f:
            loaded_json = json.load(f)

        self.config = RIDTConfig(loaded_json)
        self.config.consistency_check()

        self.pp = PointPlot(self.config, "tests/unittests/test_resources", "concentration")

        self.time_array = np.linspace(0, 10, 10)
        self.conc = np.linspace(0, 10, 10)
        self.points = self.config.models.eddy_diffusion.monitor_locations.points

    def tearDown(self) -> None:

        """tearDown method which removes and changes made in the
        tests."""

        resource_list = os.listdir("tests/unittests/test_resources")
        for file in resource_list:
            if file.endswith(".pdf"):
                os.remove(f"tests/unittests/test_resources/{file}")

if __name__ == "__main__":
    unittest.main()
