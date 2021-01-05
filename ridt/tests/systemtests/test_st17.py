import unittest
import os
from os import listdir
from os.path import join
from os import remove
import shutil
from numpy import squeeze
from pathlib import Path

from ridt.config import ConfigFileParser

from ridt.equation import EddyDiffusion

from ridt.container import Domain
from ridt.container.eddydiffusionrun import EddyDiffusionRun

from ridt.data import BatchDataStore


class ST17(unittest.TestCase):

    """System Test 17. test the system can use
       the information in the parsed JSON configuration
       file to evaluate the specified Eddy Diffusion model
       for all times, monitor locations, full domain, and
       points in parameter space (as defined by the ranges
       in the configuration file)."""

    def setUp(self) -> None:

        this_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(this_dir, "st17")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        with ConfigFileParser(os.path.join(this_dir, "st16/explicit.json")) as cfp:
            self.c = cfp

        self.bds = BatchDataStore()
        self.domain = Domain(self.c)
        self.edr = EddyDiffusionRun(self.c, self.output_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.output_dir)

    def test_verify(self):

        for val in self.edr.data_store.store.values():
            for point in val.points.values():
                self.assertEqual(len(point), self.c.time_samples)
            for line_name, line in val.lines.items():
                monitor = self.c.models.eddy_diffusion.monitor_locations.lines[line_name]
                axis = getattr(monitor, "parallel_axis")
                shape = (self.c.time_samples, getattr(self.c.spatial_samples, axis))
                self.assertEqual(line.shape, shape)
            for plane_name, plane in val.planes.items():
                monitor = self.c.models.eddy_diffusion.monitor_locations.planes[plane_name]
                axis = getattr(monitor, "axis")
                shape = [self.c.time_samples, 0, 0]
                for i, dim in enumerate(list(axis)):
                    shape[i + 1] = getattr(self.c.spatial_samples, dim)
                shape = tuple(shape)
                self.assertEqual(plane.shape, shape)


if __name__ == "__main__":
    unittest.main()
