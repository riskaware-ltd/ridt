import unittest

import os

from ridt.config import ConfigFileParser


class ST08(unittest.TestCase):

    """System Test 08. Test that the system can
       parse the options relating to the number of
       image sources and allowable error for the
       Eddy diffusion model from the JSON file."""

    def setUp(self) -> None:

        this_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(this_dir, "../../default/config.json")
        with ConfigFileParser(path) as cfp:
            self.c = cfp

    def test_verify(self):

        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion, "images"), True
        )
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.images, "quantity"), True
        )


if __name__ == "__main__":
    unittest.main()
