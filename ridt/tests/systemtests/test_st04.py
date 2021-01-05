import unittest

import os

from ridt.config import ConfigFileParser


class ST04(unittest.TestCase):

    """System Test 04. Test that the system is
       able to parse all physical parameters
       defined in the user requirements from
       the JSON file."""

    def setUp(self) -> None:

        """setUp method which instantiates an
        :class:`~.RIDTConfig` class."""

        this_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(this_dir, "../../default/config.json")
        with ConfigFileParser(path) as cfp:
            self.c = cfp

    def test_verify(self):

        """Verify that the :class:`~.RIDTConfig` class contains
        the correct attribute."""

        self.assertEqual(
            hasattr(self.c, "eddy_diffusion"), True)
        self.assertEqual(
            hasattr(self.c, "well_mixed"), True)
        self.assertEqual(
            hasattr(self.c, "time_samples"), True)
        self.assertEqual(
            hasattr(self.c, "total_time"), True)
        self.assertEqual(
            hasattr(self.c, "fresh_air_flow_rate_units"), True)
        self.assertEqual(
            hasattr(self.c, "fresh_air_flow_rate"), True)
        self.assertEqual(
            hasattr(self.c, "modes"), True)
        self.assertEqual(
            hasattr(self.c, "models"), True)


if __name__ == "__main__":
    unittest.main()
