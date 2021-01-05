import unittest

import os

import numpy as np

from ridt.config import ConfigFileParser

from ridt.equation import WellMixed


class ST15(unittest.TestCase):

    """System Test 15. Test the system can use the
       information in the parsed JSON configuration
       file to evaluate the specified Well Mixed
       model for all times and points in parameter
       space (as defined by the ranges in the configuration file)."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.RIDTConfig` class and the
           :class:`~.ComputationalSpace` class."""

        this_dir = os.path.dirname(os.path.abspath(__file__))
        with ConfigFileParser(os.path.join(this_dir, "st15/config.json")) as cfp:
            self.c = cfp

        self.time_array = np.linspace(
            0, self.c.total_time, self.c.time_samples
        )

        self.wm = WellMixed(self.c)

    def test_verify(self):
        conc = self.wm(self.time_array)
        self.assertEqual(
            len(conc), len(self.time_array)
        )


if __name__ == "__main__":
    unittest.main()
