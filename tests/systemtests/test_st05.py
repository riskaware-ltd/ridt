import unittest

from config import ConfigFileParser


class ST05(unittest.TestCase):

    """System Test 05. Verify that the system can
       parse all plotting options from the JSON file,
       for point, line, plane monitor points."""

    def setUp(self) -> None:

        """setUp method that instantiates the
        :class:`~.IDMFConfig` class."""

        with ConfigFileParser("default/config.json") as cfp:
            self.c = cfp

    def test_verify(self):

        """Verifies that the :class:`~.ModelSettings` class
        contains the correct the attributes."""

        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion, "point_plots"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion, "line_plots"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion, "contour_plots"), True)

    def test_point_plots(self):

        """Verifies that the :class:`~.PointPlots` class
        contains the correct the attributes."""

        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.point_plots, "output"), True)

    def test_line_plots(self):

        """Verifies that the :class:`~.LinePlots` class
        contains the correct the attributes."""

        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.line_plots, "output"), True)

    def test_contour_plots(self):

        """Verifies that the :class:`~.ContourPlots` class
        contains the correct the attributes."""

        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.contour_plots, "output"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.contour_plots, "concentration"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.contour_plots, "exposure"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.contour_plots, "creation_frequency"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.contour_plots, "number_of_contours"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.contour_plots, "range"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.contour_plots, "scale"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.contour_plots.contours, "min"), True)
        self.assertEqual(
            hasattr(self.c.models.eddy_diffusion.contour_plots.contours, "max"), True)


if __name__ == "__main__":
    unittest.main()
