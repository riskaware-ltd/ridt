import unittest
import json

import numpy as np

from config import IDMFConfig
from equation import WellMixed


class TestWellMixed(unittest.TestCase):

    def setUp(self) -> None:
        with open("tests/test_resources/test_config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)
        self.config.consistency_check()

        self.wm = WellMixed(self.config)

    def test_concentration(self):

        for time in range(10):
            exp = self.wm.concentration(time)

            value = np.exp(-time)

            self.assertEqual(exp, value)
            self.assertEqual(type(exp), np.float64)

    def test_outputs(self):
        time_array = np.linspace(0, 10, 10)
        inst_conc = self.wm(time_array)
        self.assertEqual(type(inst_conc), np.ndarray)
