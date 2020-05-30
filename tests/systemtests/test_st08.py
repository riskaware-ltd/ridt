import unittest

from config import ConfigFileParser


class ST08(unittest.TestCase):

    """System Test 08. Test that the system can
       parse the options relating to the number of
       image sources and allowable error for the
       Eddy diffusion model from the JSON file."""

    def setUp(self) -> None:

        """setUp method that instantiates the
          :class:`~.IDMFConfig` class."""

        with ConfigFileParser("default/config.json") as cfp:
            self.c = cfp

    def test_verify(self):

        """Verify that the :class:`~.EddyDiffusion` class
        contains the correct Image attributes."""

        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion, "images"), True
        )
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.images, "quantity"), True
        )


if __name__ == "__main__":
    unittest.main()
