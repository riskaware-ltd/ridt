import unittest
import json

import numpy as np

from ridt.config import RIDTConfig
from ridt.equation import EddyDiffusion


class TestEddyDiffusion(unittest.TestCase):

    def setUp(self) -> None:


        with open("tests/unittests/test_resources/test_config.json") as f:
            loaded_json = json.load(f)

        self.config = RIDTConfig(loaded_json)

        self.ed = EddyDiffusion(self.config)

        self.time_array = np.linspace(0, 10, 10)
        self.x_space = np.linspace(0, 10, 10)
        self.y_space = np.linspace(0, 10, 10)
        self.z_space = np.linspace(0, 10, 10)

    def test_outputs(self):

        """Ensures the concentration is of type array"""

        concentration = self.ed(
            self.x_space, self.y_space, self.z_space, self.time_array
        )
        self.assertEqual(type(concentration), np.ndarray)


if __name__ == "__main__":
    unittest.main()
