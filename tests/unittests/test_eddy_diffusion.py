import unittest
import json

import numpy as np

from config import IDMFConfig
from equation import EddyDiffusion


class TestEddyDiffusion(unittest.TestCase):

    def setUp(self) -> None:

        """setUp method which instantiates the :class:`~.IDMFConfig` class,
        the :class:`~.EddyDiffusion` class, and creates some initial
        variables."""

        with open("tests/unittests/test_resources/test_config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)

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

    def test__coeff(self):

        """Tests the output of the coefficient under certain
        conditions."""

        coeff = self.ed._EddyDiffusion__coeff(1)
        self.assertEqual(
            coeff, 1 / (8 * np.power(np.pi, 3/2) * np.exp(1))
        )

    def test_diffusion_coefficient(self):

        """Ensures the correct output type of the coefficients."""

        self.ed.settings.models.eddy_diffusion.coefficient.calculation = "EXPLICIT"
        self.assertEqual(
            type(self.ed._EddyDiffusion__diffusion_coefficient()), float
        )
        self.ed.settings.models.eddy_diffusion.coefficient.calculation = "VALUE"
        self.assertEqual(
            type(self.ed._EddyDiffusion__diffusion_coefficient()), np.float64
        )

    def test_exp(self):

        """"Makes sure that the exp function is
        operating correctly."""

        bound = 1
        source_loc = 1
        t = 1
        rv = self.ed._EddyDiffusion__exp(
            self.x_space, t, bound, source_loc
        )
        self.assertEqual(type(rv), np.ndarray)

    def test_concentration(self):

        """Makes sure that the concentration function outputs
        the correct type."""

        self.ed.sources = getattr(self.ed.settings.modes, "fixed_duration").sources
        time = 1
        for source in self.ed.sources.values():
            self.assertEqual(
                type(self.ed._EddyDiffusion__concentration(source, self.x_space, self.y_space, self.z_space, time)),
                np.ndarray
            )


if __name__ == "__main__":
    unittest.main()
