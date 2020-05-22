import unittest

from numpy import squeeze

from config import ConfigFileParser

from equation import EddyDiffusion

from container import Domain

from data import BatchDataStore


class ST17(unittest.TestCase):

    """System Test 17. test the system can use
       the information in the parsed JSON configuration
       file to evaluate the specified Eddy Diffusion model
       for all times, monitor locations, full domain, and
       points in parameter space (as defined by the ranges
       in the configuration file)."""

    def setUp(self) -> None:

        with ConfigFileParser("tests/systemtests/st16/explicit.json") as cfp:
            self.c = cfp

        self.bds = BatchDataStore()
        self.domain = Domain(self.c)
        self.ed = EddyDiffusion(self.c)

    def test_verify(self):

        self.bds.add_run(self.c)
        points = self.c.models.eddy_diffusion.monitor_locations.points
        lines = self.c.models.eddy_diffusion.monitor_locations.lines
        planes = self.c.models.eddy_diffusion.monitor_locations.planes

        for point_name, point in points.items():
            output = self.ed(*self.domain.point(point), self.domain.time)
            self.bds[self.c].add_point_data(point_name, squeeze(output))

        for line_name, line in lines.items():
            output = self.ed(*self.domain.line(line), self.domain.time)
            self.bds[self.c].add_line_data(line_name, squeeze(output))

        for plane_name, plane in planes.items():
            output = self.ed(*self.domain.plane(plane), self.domain.time)
            self.bds[self.c].add_plane_data(plane_name, squeeze(output))

        output = self.ed(*self.domain.full, self.domain.time)
        self.bds[self.c].add_domain_data(output)

        for point in self.bds[self.c].points.values():
            self.assertEqual(len(point), self.c.time_samples)

        for key, line in self.bds[self.c].lines.items():
            monitor = self.c.models.eddy_diffusion.monitor_locations.lines[key]
            axis = getattr(monitor, "parallel_axis")
            shape = (self.c.time_samples, getattr(self.c.models.eddy_diffusion.spatial_samples, axis))
            self.assertEqual(line.shape, shape)

        for key, plane in self.bds[self.c].planes.items():
            monitor = self.c.models.eddy_diffusion.monitor_locations.planes[key]
            axis = getattr(monitor, "axis")
            shape = [self.c.time_samples, 0, 0]
            for i, dim in enumerate(list(axis)):
                shape[i + 1] = getattr(self.c.models.eddy_diffusion.spatial_samples, dim)
            shape = tuple(shape)
            self.assertEqual(plane.shape, shape)


if __name__ == "__main__":
    unittest.main()
