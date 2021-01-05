import unittest

import os

import numpy as np

from ridt.config import ConfigFileParser

from ridt.equation import EddyDiffusion


class ST16(unittest.TestCase):

    """System Test 16. Test that the system can
       evaluate the TKEB diffusion coefficient
       and use it in the Eddy Diffusion model."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.RIDTConfig` class and the
           :class:`~.ComputationalSpace` class."""

        this_dir = os.path.dirname(os.path.abspath(__file__))
        with ConfigFileParser(os.path.join(this_dir, "st16/explicit.json")) as cfp:
            self.e = cfp
        with ConfigFileParser(os.path.join(this_dir, "st16/tkeb.json")) as cfp:
            self.t = cfp

        self.explicit = EddyDiffusion(self.e)
        self.tkeb = EddyDiffusion(self.t)

    def test_verify(self):
        self.assertEqual(
            self.explicit.diffusion_coefficient(), 0.001
        )
        self.assertEqual(
            self.tkeb.diffusion_coefficient(), 0.7655
        )


if __name__ == "__main__":
    unittest.main()
