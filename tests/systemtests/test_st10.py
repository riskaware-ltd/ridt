import unittest

from config import ConfigFileParser


class ST10(unittest.TestCase):

    """System Test 10. Test the system can
       parse the user’s choice of diffusion
       coefficient from the JSON file."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.RIDTConfig` class."""

        with ConfigFileParser("default/config.json") as cfp:
            self.c = cfp

    def test_verify(self):

        """Verify that the :class:`~.EddyDiffusion` class has
        the correct attributes."""

        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion, "coefficient"), True
        )
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.coefficient, "calculation"), True
        )
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.coefficient, "value"), True
        )
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.coefficient, "tkeb"), True
        )
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.coefficient.tkeb, "number_of_supply_vents"), True
        )


if __name__ == "__main__":
    unittest.main()
