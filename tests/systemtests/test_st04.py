import unittest

from config import ConfigFileParser


class ST04(unittest.TestCase):

    """System Test 04. Test that the system is
       able to parse all physical parameters
       defined in the user requirements from
       the JSON file."""

    def setUp(self) -> None:

        """setUp method which instantiates an
        :class:`~.IDMFConfig` class."""

        with ConfigFileParser("default/config.json") as cfp:
            self.c = cfp

    def test_verify(self):

        """Verify that the :class:`~.IDMFConfig` class contains
        the correct attribute."""

        self.assertEqual(
            hasattr(self.c, "dispersion_model"), True)
        self.assertEqual(
            hasattr(self.c, "time_samples"), True)
        self.assertEqual(
            hasattr(self.c, "total_time"), True)
        self.assertEqual(
            hasattr(self.c, "total_air_change_rate"), True)
        self.assertEqual(
            hasattr(self.c, "fresh_air_change_rate"), True)
        self.assertEqual(
            hasattr(self.c, "human_readable_data_output"), True)
        self.assertEqual(
            hasattr(self.c, "modes"), True)
        self.assertEqual(
            hasattr(self.c, "models"), True)


if __name__ == "__main__":
    unittest.main()
