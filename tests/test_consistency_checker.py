import unittest
import json

from config import IDMFConfig
from config import ConsistencyError


class TestConsistencyChecker(unittest.TestCase):

    def setUp(self) -> None:
        with open("default/config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)

    def test_dispersion_model(self):
        self.config.dispersion_model = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.config.consistency_check)

    def test_source_times(self):
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
        for i in range(6):
            self.config.thresholds.concentration.append(1)
        self.assertRaises(ConsistencyError, self.config.consistency_check)

        for i in range(6):
            self.config.thresholds.exposure.append(1)
        self.assertRaises(ConsistencyError, self.config.consistency_check)

    def test_planes(self):
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
        self.config.time_units = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.config.consistency_check)

    def test_spatial_units(self):
        self.config.models.eddy_diffusion.spatial_units = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.config.consistency_check)

    def test_concentration_units(self):
        self.config.concentration_units = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.config.consistency_check)

    def test_exposure_units(self):
        self.config.exposure_units = "RANDOM VALUE"
        self.assertRaises(ConsistencyError, self.config.consistency_check)


if __name__ == "__main__":
    unittest.main()
