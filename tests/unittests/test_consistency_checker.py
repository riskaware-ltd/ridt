import unittest
import json

from config import IDMFConfig
from config import ConsistencyError


class TestConsistencyChecker(unittest.TestCase):

    """Unit tests for the :meth:`~.consistency_check` method of
    the :class:`~.IDMFConfig` class."""

    def setUp(self) -> None:

        """setUp method which instantiates the
        :class:`~.IDMFConfig` class."""

        with open("default/config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)

    def test_dispersion_model(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers when given a random string for the dispersion model."""

        self.config.dispersion_model = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.config.consistency_check)

    def test_source_times(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers when the time of a source is greater than
        the total time of the simulation."""

        for key, value in self.config.modes.instantaneous.sources.items():
            value.time = self.config.total_time + 1
            self.assertRaises(ConsistencyError, self.config.consistency_check)

        for key, value in self.config.modes.infinite_duration.sources.items():
            value.time = self.config.total_time + 1
            self.assertRaises(ConsistencyError, self.config.consistency_check)

        for key, value in self.config.modes.fixed_duration.sources.items():
            value.start_time = self.config.total_time + 1
            self.assertRaises(ConsistencyError, self.config.consistency_check)

        for key, value in self.config.modes.fixed_duration.sources.items():
            value.start_time = value.end_time + 1
            self.assertRaises(ConsistencyError, self.config.consistency_check)

    def test_thresholds(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers when the number of thresholds exceeds 5."""

        for i in range(6):
            self.config.thresholds.concentration.append(1)
        self.assertRaises(ConsistencyError, self.config.consistency_check)

        for i in range(6):
            self.config.thresholds.exposure.append(1)
        self.assertRaises(ConsistencyError, self.config.consistency_check)

    def test_planes(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if a plane lies outside of the bounds of the container."""

        ed = self.config.models.eddy_diffusion
        for key, val in ed.monitor_locations.planes.items():
            if val.axis == "xy":
                val.distance = ed.dimensions.z + 1
                self.assertRaises(ConsistencyError, self.config.consistency_check)
            if val.axis == "xz":
                val.distance = ed.dimensions.y + 1
                self.assertRaises(ConsistencyError, self.config.consistency_check)
            if val.axis == "zy":
                val.distance = ed.dimensions.x + 1
                self.assertRaises(ConsistencyError, self.config.consistency_check)
            val.axis = "RANDOM VALUE"
            self.assertRaises(ConsistencyError, self.config.consistency_check)

    def test_contours(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the min value of the contour is greater than
        max value. Or if the string passed as the scale or range
        doesn't match the pre defined values."""

        c_plots = self.config.models.eddy_diffusion.contour_plots

        c_plots.contours.min = c_plots.contours.max + 1
        self.assertRaises(ConsistencyError, self.config.consistency_check)

        c_plots.contours.min = c_plots.contours.max - 1

        c_plots.range = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.config.consistency_check)

        c_plots.range = "auto"

        c_plots.scale = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.config.consistency_check)

    def test_time_units(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the time units are not s, m, h."""

        self.config.time_units = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.config.consistency_check)

    def test_spatial_units(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the spatial units are not one of the pre defined
        units."""

        self.config.models.eddy_diffusion.spatial_units = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.config.consistency_check)

    def test_concentration_units(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the concentration units are not one of the pre defined
        units."""

        self.config.concentration_units = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.config.consistency_check)

    def test_exposure_units(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers if the exposure units are not one of the pre defined
        units."""

        self.config.exposure_units = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.config.consistency_check)


if __name__ == "__main__":
    unittest.main()
