import unittest

import numpy as np

from config import ConfigFileParser

from equation import WellMixed


class ST15(unittest.TestCase):

    """System Test 15. Test the system can use the
       information in the parsed JSON configuration
       file to evaluate the specified Well Mixed
       model for all times and points in parameter
       space (as defined by the ranges in the configuration file)."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.IDMFConfig` class and the
           :class:`~.ComputationalSpace` class."""

        with ConfigFileParser("tests/systemtests/st15/config.json") as cfp:
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
