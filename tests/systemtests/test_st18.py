import unittest
import os

from numpy import squeeze
from numpy import load

from config import ConfigFileParser

from equation import EddyDiffusion

from container import Domain

from data import BatchDataStore
from data import BatchDataStoreWriter

from base import ComputationalSpace


class ST18(unittest.TestCase):

    """System Test 18. test the system can
       write all data output by the models to
       a given directory."""

    def setUp(self) -> None:

        with ConfigFileParser("tests/systemtests/st16/explicit.json") as cfp:
            self.c = cfp

        self.bds = BatchDataStore()
        self.domain = Domain(self.c)
        self.ed = EddyDiffusion(self.c)

        restrict = {"models": self.c.dispersion_model}
        self.space = ComputationalSpace(self.c, restrict)
        self.output_dir = "tests/systemtests/st18"

        self.bds.add_run(self.c)
        self.points = self.c.models.eddy_diffusion.monitor_locations.points
        self.lines = self.c.models.eddy_diffusion.monitor_locations.lines
        self.planes = self.c.models.eddy_diffusion.monitor_locations.planes

        for point_name, point in self.points.items():
            output = self.ed(*self.domain.point(point), self.domain.time)
            self.bds[self.c].add_point_data(point_name, squeeze(output))

        for line_name, line in self.lines.items():
            output = self.ed(*self.domain.line(line), self.domain.time)
            self.bds[self.c].add_line_data(line_name, squeeze(output))

        for plane_name, plane in self.planes.items():
            output = self.ed(*self.domain.plane(plane), self.domain.time)
            self.bds[self.c].add_plane_data(plane_name, squeeze(output))

        output = self.ed(*self.domain.full, self.domain.time)
        self.bds[self.c].add_domain_data(output)

    def tearDown(self) -> None:
        for item in self.list_dir:
            path = os.path.join(self.output_dir, item)
            os.remove(path)

    def test_write(self):

        with BatchDataStoreWriter(self.c,
                                  self.bds,
                                  self.space) as dsw:
            dsw.write(self.output_dir)

        self.list_dir = os.listdir(self.output_dir)

        for point_name, point in self.points.items():
            self.assertIn(f"{point_name}.npy", self.list_dir)
        for line_name, line in self.lines.items():
            self.assertIn(f"{line_name}.npy", self.list_dir)
        for plane_name, plane in self.planes.items():
            self.assertIn(f"{plane_name}.npy", self.list_dir)
        self.assertIn(f"domain.npy", self.list_dir)


if __name__ == "__main__":
    unittest.main()
