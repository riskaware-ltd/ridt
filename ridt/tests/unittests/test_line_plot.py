import unittest
import json
import os

import numpy as np
from matplotlib.lines import Line2D

from ridt.config import RIDTConfig
from ridt.plot import LinePlot


class TestLinePlot(unittest.TestCase):

    "Unit tests for the :class:`~.LinePlot` class."""

    def setUp(self) -> None:

        """setUp method which instantiates the :class:`~.RIDTConfig` class,
        the :class:`~.LinePlot` class, and creates some initial
        variables."""

        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(self.this_dir, "test_resources/test_config.json")) as f:
            loaded_json = json.load(f)

        self.config = RIDTConfig(loaded_json)

        self.lp = LinePlot(self.config, os.path.join(self.this_dir, "test_resources", "concentration"))

        self.time_array = np.linspace(0, 10, 10)
        self.conc = np.linspace(0, 10, 10)
        self.lines = self.config.models.eddy_diffusion.monitor_locations.lines

    def tearDown(self) -> None:

        """tearDown method which removes and changes made in the
        tests."""

        resource_list = os.listdir(os.path.join(self.this_dir, "test_resources"))
        for file in resource_list:
            if file.endswith(".pdf"):
                os.remove(os.path.join(self.this_dir, f"test_resources/{file}"))


if __name__ == "__main__":
    unittest.main()
