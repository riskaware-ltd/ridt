import unittest
import json
import os

import numpy as np
from matplotlib.lines import Line2D

from config import IDMFConfig
from plot import LinePlot


class TestLinePlot(unittest.TestCase):

    "Unit tests for the :class:`~.LinePlot` class."""

    def setUp(self) -> None:

        """setUp method which instantiates the :class:`~.IDMFConfig` class,
        the :class:`~.LinePlot` class, and creates some initial
        variables."""

        with open("tests/unittests/test_resources/test_config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)

        self.lp = LinePlot(self.config, "tests/unittests/test_resources")

        self.time_array = np.linspace(0, 10, 10)
        self.conc = np.linspace(0, 10, 10)
        self.lines = self.config.models.eddy_diffusion.monitor_locations.lines

    def tearDown(self) -> None:

        """tearDown method which removes and changes made in the
        tests."""

        resource_list = os.listdir("tests/unittests/test_resources")
        for file in resource_list:
            if file.endswith(".pdf"):
                os.remove(f"tests/unittests/test_resources/{file}")

    def test_plot(self):

        """tests the plots to make sure that is plot is
        of type :class:`~.Line2D.`"""

        for line in self.lines.values():
            plots = self.lp.plot(self.conc, line)
            for plot in plots:
                self.assertEqual(type(plot), Line2D)

    def test_make_title(self):

        """tests to make sure that the title
        is of type :obj:`str`."""

        for line in self.lines.values():
            title = self.lp.make_title(line)
            self.assertEqual(type(title), str)


if __name__ == "__main__":
    unittest.main()
