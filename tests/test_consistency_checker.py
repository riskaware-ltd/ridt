import unittest
import json

from config import IDMFConfig


class TestConsistencyChecker(unittest.TestCase):

    def setUp(self) -> None:
        with open("../default/config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)
        self.config.consistency_check()

    def test_dispersion_model(self):
        self.config.dispersion_model = "RANDOM VALUE"
        self.assertRaises(ValueError, self.config.consistency_check)

    def test_release_type(self):
        self.config.release_type = "RANDOM VALUE"
        self.assertRaises(ValueError, self.config.consistency_check)

    def test_source_times(self):
        for key, value in self.config.modes.instantaneous.sources.items():
            value.time = self.config.total_time + 1
            self.assertRaises(ValueError, self.config.consistency_check)

        for key, value in self.config.modes.infinite_duration.sources.items():
            value.time = self.config.total_time + 1
            self.assertRaises(ValueError, self.config.consistency_check)

        for key, value in self.config.modes.fixed_duration.sources.items():
            value.start_time = self.config.total_time + 1
            self.assertRaises(ValueError, self.config.consistency_check)

        for key, value in self.config.modes.fixed_duration.sources.items():
            value.start_time = value.end_time + 1
            self.assertRaises(ValueError, self.config.consistency_check)

    def test_thresholds(self):
        for i in range(6):
            self.config.thresholds.concentration.append(1)
        self.assertRaises(ValueError, self.config.consistency_check)

        for i in range(6):
            self.config.thresholds.exposure.append(1)
        self.assertRaises(ValueError, self.config.consistency_check)

    def test_planes(self):
        for key, val in self.config.models.eddy_diffusion.contour_plots.planes.items():
            if val.axis == "xy":
                val.distance = self.config.models.eddy_diffusion.dimensions.z + 1
                self.assertRaises(ValueError, self.config.consistency_check)
            if val.axis == "xz":
                val.distance = self.config.models.eddy_diffusion.dimensions.y + 1
                self.assertRaises(ValueError, self.config.consistency_check)
            if val.axis == "zy":
                val.distance = self.config.models.eddy_diffusion.dimensions.x + 1
                self.assertRaises(ValueError, self.config.consistency_check)
            val.axis = "RANDOM VALUE"
            self.assertRaises(ValueError, self.config.consistency_check)

    def test_contours(self):
        self.config.models.eddy_diffusion.contour_plots.contours.min = \
            self.config.models.eddy_diffusion.contour_plots.contours.max + 1
        self.assertRaises(ValueError, self.config.consistency_check)

        self.config.models.eddy_diffusion.contour_plots.contours.min = \
            self.config.models.eddy_diffusion.contour_plots.contours.max - 1

        self.config.models.eddy_diffusion.contour_plots.range = "RANDOM VALUE"
        self.assertRaises(ValueError, self.config.consistency_check)

        self.config.models.eddy_diffusion.contour_plots.range = "auto"

        self.config.models.eddy_diffusion.contour_plots.scale = "RANDOM VALUE"
        self.assertRaises(ValueError, self.config.consistency_check)

    def test_time_units(self):
        self.config.time_units = "RANDOM VALUE"
        self.assertRaises(ValueError, self.config.consistency_check)

    def test_spatial_units(self):
        self.config.spatial_units = "RANDOM VALUE"
        self.assertRaises(ValueError, self.config.consistency_check)

    def test_concentration_units(self):
        self.config.concentration_units = "RANDOM VALUE"
        self.assertRaises(ValueError, self.config.consistency_check)

    def test_exposure_units(self):
        self.config.exposure_units = "RANDOM VALUE"
        self.assertRaises(ValueError, self.config.consistency_check)


if __name__ == "__main__":
    unittest.main()
