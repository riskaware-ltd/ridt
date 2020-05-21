import unittest

from config import ConfigFileParser
from config import ConsistencyError


class ST06(unittest.TestCase):

    """System Test 06. Test that the system can parse
     all physical unit specifications from the JSON file."""

    def setUp(self) -> None:

        """setUp method that instantiates the
        :class:`~.IDMFConfig` class."""

        with ConfigFileParser("default/config.json") as cfp:
            self.c = cfp

    def test_verify(self):

        """Verifies that the :class:`~.IDMFConfig` class
        contains the correct the attributes."""

        self.assertEqual(
            hasattr(self.c, "time_units"), True)
        self.assertEqual(
            hasattr(self.c, "concentration_units"), True)
        self.assertEqual(
            hasattr(self.c, "exposure_units"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion, "spatial_units"), True
        )

    def test_time_units(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the time units are not s, m, h."""

        self.c.time_units = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.c.consistency_check)

    def test_spatial_units(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the spatial units are not one of the pre defined
        units."""

        self.c.models.eddy_diffusion.spatial_units = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.c.consistency_check)

    def test_concentration_units(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the concentration units are not one of the pre defined
        units."""

        self.c.concentration_units = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.c.consistency_check)

    def test_exposure_units(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the exposure units are not one of the pre defined
        units."""

        self.c.exposure_units = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.c.consistency_check)


if __name__ == "__main__":
    unittest.main()
