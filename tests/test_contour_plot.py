import unittest
import json
import os

import numpy as np
from matplotlib.contour import QuadContourSet

from config import IDMFConfig
from analysis import ContourPlot


class TestPointPlot(unittest.TestCase):

    def setUp(self) -> None:

        with open("test_resources/test_config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)
        self.config.consistency_check()

        self.cp = ContourPlot(self.config)

        self.time_array = np.linspace(0, 10, 10)
        self.x_array = np.linspace(0, 10, 10)
        self.conc, _ = np.meshgrid(self.x_array, self.x_array)
        self.save_dir = "test_resources"
        self.planes = self.config.models.eddy_diffusion.monitor_locations.planes

    def tearDown(self) -> None:
        resource_list = os.listdir("test_resources")
        for file in resource_list:
            if file.endswith(".pdf"):
                os.remove(f"test_resources/{file}")

    def test_plot(self):
        for plane in self.planes.values():
            plot = self.cp.plot(self.conc, plane)
            self.assertEqual(type(plot), QuadContourSet)

    def test_make_title(self):
        for plane in self.planes.values():
            title = self.cp.make_title(plane)
            self.assertEqual(type(title), str)


if __name__ == "__main__":
    unittest.main()
