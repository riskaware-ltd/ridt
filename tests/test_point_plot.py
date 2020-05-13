import unittest
import json
import os

import numpy as np
from matplotlib.lines import Line2D

from config import IDMFConfig
from plot import PointPlot


class TestPointPlot(unittest.TestCase):

    def setUp(self) -> None:

        with open("tests/test_resources/test_config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)
        self.config.consistency_check()

        self.pp = PointPlot(self.config, "tests/test_resources")

        self.time_array = np.linspace(0, 10, 10)
        self.conc = np.linspace(0, 10, 10)
        self.points = self.config.models.eddy_diffusion.monitor_locations.points

    def tearDown(self) -> None:
        resource_list = os.listdir("tests/test_resources")
        for file in resource_list:
            if file.endswith(".pdf"):
                os.remove(f"tests/test_resources/{file}")

    def test_plot(self):
        plots = self.pp.plot(self.conc)

        for plot in plots:
            self.assertEqual(type(plot), Line2D)

    def test_make_title(self):
        title = self.pp.make_title()
        self.assertEqual(type(title), str)


if __name__ == "__main__":
    unittest.main()
