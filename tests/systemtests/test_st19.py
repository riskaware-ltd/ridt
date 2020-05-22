import unittest

import numpy as np

from config import ConfigFileParser

from plot import LinePlot


class ST19(unittest.TestCase):

    """System Test 19. test the system can
       produce line plots of data where requested."""

    def setUp(self) -> None:

        with ConfigFileParser("tests/systemtests/st16/explicit.json") as cfp:
            self.c = cfp

        self.lp = LinePlot(self.c, "tests/systemtests/st19")

        self.time_array = self.lp.time_array

    def test_verify(self):
        concentrations = []
        for time in self.time_array:
            concentrations.append(self.time_array * np.power(time, 10))
        for line in self.c.models.eddy_diffusion.monitor_locations.lines.values():
            print(concentrations)
            for concentration in concentrations:
                self.lp(concentration, line)


if __name__ == "__main__":
    unittest.main()
