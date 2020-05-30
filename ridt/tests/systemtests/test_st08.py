import unittest

from ridt.config import ConfigFileParser


class ST08(unittest.TestCase):

    """System Test 08. Test that the system can
       parse the options relating to the number of
       image sources and allowable error for the
       Eddy diffusion model from the JSON file."""

    def setUp(self) -> None:

        with ConfigFileParser("default/config.json") as cfp:
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
