import unittest

from ridt.config import ConfigFileParser


class ST05(unittest.TestCase):

    """System Test 05. Verify that the system can
       parse all plotting options from the JSON file,
       for point, line, plane monitor points."""

    def setUp(self) -> None:

        """setUp method that instantiates the
        :class:`~.RIDTConfig` class."""

        with ConfigFileParser("default/config.json") as cfp:
            self.c = cfp

    def test_verify(self):

        """Verifies that the :class:`~.ModelSettings` class
        contains the correct the attributes."""

        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion, "points_plots"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion, "lines_plots"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion, "planes_plots"), True)

    def test_point_plots(self):

        """Verifies that the :class:`~.PointPlots` class
        contains the correct the attributes."""

        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.points_plots, "output"), True)

    def test_line_plots(self):

        """Verifies that the :class:`~.LinePlots` class
        contains the correct the attributes."""

        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.lines_plots, "output"), True)

    def test_contour_plots(self):

        """Verifies that the :class:`~.ContourPlots` class
        contains the correct the attributes."""

        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.planes_plots, "output"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.planes_plots, "number_of_contours"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.planes_plots, "range"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.planes_plots, "scale"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.planes_plots.contours, "min"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.planes_plots.contours, "max"), True)


if __name__ == "__main__":
    unittest.main()
