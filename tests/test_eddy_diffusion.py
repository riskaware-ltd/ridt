import unittest
import json

import numpy as np

from config import IDMFConfig
from equation import EddyDiffusion


class TestWellMixed(unittest.TestCase):

    def setUp(self) -> None:
        with open("test_resources/test_config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)
        self.config.consistency_check()

        self.ed = EddyDiffusion(self.config)

    def test_coeff(self):
        time_array = np.linspace(0, 1, 10)
        concentration = self.ed._EddyDiffusion__coeff(time_array)
        self.assertEqual(type(concentration), np.ndarray)

    def test_instantaneous(self):
        self.ed.sources = getattr(self.ed.settings.modes, "instantaneous").sources
        time_array = np.linspace(0, 10, 10)
        x_space = np.linspace(0, 10, 10)
        y_space = np.linspace(0, 10, 10)
        z_space = np.linspace(0, 10, 10)

        concentration = self.ed.instantaneous(x_space, y_space, z_space, time_array)
        print(concentration)

    def test_infinite(self):
        self.wm.sources = getattr(self.wm.settings.modes, "infinite_duration").sources
        time_array = np.linspace(0, 10, 10)
        concentration = 1 - np.exp(-time_array)
        inf_conc = self.wm.infinite_duration(time_array)
        for idx, value in enumerate(concentration):
            self.assertEqual(
                inf_conc[idx], value
            )
            self.assertEqual(type(inf_conc[idx]), np.float64)
        self.assertEqual(type(inf_conc), np.ndarray)

    def test_fixed(self):
        self.wm.sources = getattr(self.wm.settings.modes, "fixed_duration").sources
        time_array = np.linspace(0, 1, 10)
        concentration = np.zeros(time_array.shape)
        for idx, time in enumerate(time_array):
            for source in self.wm.sources.values():
                if time - source.start_time < 0:
                    concentration[idx] += 0
                if source.start_time <= time <= source.end_time:
                    concentration[idx] += 1 - np.exp(-(time - source.start_time))
                if time > source.end_time:
                    concentration[idx] += concentration[4] * \
                        np.exp(-(time - source.end_time))

        fixed_conc = self.wm.fixed_duration(time_array)

        for idx, value in enumerate(concentration):
            self.assertEqual(
                fixed_conc[idx], value
            )
            self.assertEqual(type(fixed_conc[idx]), np.float64)
        self.assertEqual(type(fixed_conc), np.ndarray)


if __name__ == "__main__":
    unittest.main()
