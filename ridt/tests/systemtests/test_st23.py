import unittest
import os
from os import listdir
from os.path import join
from os import remove
import shutil
from pathlib import Path

from ridt.config import ConfigFileParser

from ridt.container import Domain
from ridt.container.eddydiffusionrun import EddyDiffusionRun

from ridt.data import BatchDataStore


class ST23(unittest.TestCase):

    """System Test 23. Test the system can
       output all data generated during a
       run to CSV files in an output directory."""

    def setUp(self) -> None:

        this_dir = os.path.dirname(os.path.abspath(__file__))
        with ConfigFileParser(join(this_dir, "st23/config.json")) as cfp:
            self.c = cfp

        self.bds = BatchDataStore()
        self.domain = Domain(self.c)
        self.output_dir = join(this_dir, "st23/data")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.edr = EddyDiffusionRun(self.c, self.output_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.output_dir)

    def test_verify(self):
        output_types = ["concentration", "exposure"]
        geometries = ["points", "lines", "planes"]
        for output in output_types:
            for geometry in geometries:
                _path = join(self.output_dir, geometry, output, "data")
                for name, val in getattr(self.c.models.eddy_diffusion.monitor_locations, geometry).items():
                    self.assertIn(f"{name}.csv", listdir(_path))


if __name__ == "__main__":
    unittest.main()
