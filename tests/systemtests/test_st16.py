import unittest

import numpy as np

from config import ConfigFileParser

from equation import EddyDiffusion


class ST16(unittest.TestCase):

    """System Test 16. Test that the system can
       evaluate the TKEB diffusion coefficient
       and use it in the Eddy Diffusion model."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.IDMFConfig` class and the
           :class:`~.ComputationalSpace` class."""

        with ConfigFileParser("tests/systemtests/st16/explicit.json") as cfp:
            self.e = cfp
        with ConfigFileParser("tests/systemtests/st16/tkeb.json") as cfp:
            self.t = cfp

        self.explicit = EddyDiffusion(self.e)
        self.tkeb = EddyDiffusion(self.t)

    def test_verify(self):
        self.assertEqual(
            self.explicit._EddyDiffusion__diffusion_coefficient(), 0.1
        )
        self.assertEqual(
            self.tkeb._EddyDiffusion__diffusion_coefficient(), 0.824
        )


if __name__ == "__main__":
    unittest.main()
