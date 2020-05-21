import unittest

from config import ConfigFileParser
from config import ConsistencyError


class ST11(unittest.TestCase):

    """System Test 11. Test the system can convert
       config files with ranges of values into a set of
       config object, each which can be evaluated separately."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.IDMFConfig` class."""

        with ConfigFileParser("default/config.json") as cfp:
            self.c = cfp

    def test_verify(self):

        """Verify that the :class:`~.ContourPlots` class
        has the correct scale and range attributes."""

        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.contour_plots, "range"), True
        )
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.contour_plots, "scale"), True
        )

    def test_contours(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the min value of the contour is greater than
        max value. Or if the string passed as the scale or range
        doesn't match the pre defined values."""

        c_plots = self.c.models.eddy_diffusion.contour_plots

        c_plots.contours.min = c_plots.contours.max + 1
        self.assertRaises(ConsistencyError, self.c.consistency_check)

        c_plots.contours.min = c_plots.contours.max - 1

        c_plots.range = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.c.consistency_check)

        c_plots.range = "auto"

        c_plots.scale = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.c.consistency_check)


if __name__ == "__main__":
    unittest.main()
