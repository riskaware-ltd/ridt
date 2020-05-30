import unittest
import json

import numpy as np

from config import IDMFConfig
from equation import WellMixed


class TestWellMixed(unittest.TestCase):

    "Unit tests for the :class:`~.WellMixed` class."""

    def setUp(self) -> None:

        """setUp method which instantiates the :class:`~.IDMFConfig` class,
        the :class:`~.WellMixed` class, and creates some initial
        variables."""

        with open("tests/unittests/test_resources/test_config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)

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
