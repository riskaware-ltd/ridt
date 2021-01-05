import unittest

import os

from ridt.config import ConfigFileParser


class ST10(unittest.TestCase):

    """System Test 10. Test the system can
       parse the user’s choice of diffusion
       coefficient from the JSON file."""

    def setUp(self) -> None:

        this_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(this_dir, "../../default/config.json")
        with ConfigFileParser(path) as cfp:
            self.c = cfp

    def test_verify(self):

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
