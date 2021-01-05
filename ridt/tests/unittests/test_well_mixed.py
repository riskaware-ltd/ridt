import unittest
import json
import os

import numpy as np

from ridt.config import RIDTConfig
from ridt.equation import WellMixed


class TestWellMixed(unittest.TestCase):

    def setUp(self) -> None:

        this_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(this_dir, "test_resources/test_config.json")) as f:
            loaded_json = json.load(f)

        self.config = RIDTConfig(loaded_json)

        self.wm = WellMixed(self.config)

    def test_concentration(self):

        """Makes sure that the concentration function outputs
        the correct type."""

        for time in range(10):
            exp = self.wm.concentration(time)

            self.assertEqual(type(exp), np.float64)

    def test_outputs(self):

        """Ensures that the concentration output type
        is ndarray."""

        time_array = np.linspace(0, 10, 10)
        inst_conc = self.wm(time_array)
        self.assertEqual(type(inst_conc), np.ndarray)
