import unittest

import numpy as np

from config import ConfigFileParser

from equation import EddyDiffusion


class ST17(unittest.TestCase):

    """System Test 17. test the system can use
       the information in the parsed JSON configuration
       file to evaluate the specified Eddy Diffusion model
       for all times, monitor locations, full domain, and
       points in parameter space (as defined by the ranges
        in the configuration file)."""

    def setUp(self) -> None:
        pass

    def test_verify(self):
        pass


if __name__ == "__main__":
    unittest.main()
