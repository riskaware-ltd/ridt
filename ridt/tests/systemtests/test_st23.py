import unittest
from os import listdir
from os.path import join
from os import remove
import shutil

from ridt.config import ConfigFileParser

from ridt.container import Domain
from ridt.container.eddydiffusionrun import EddyDiffusionRun

from ridt.data import BatchDataStore


class ST23(unittest.TestCase):

    """System Test 23. Test the system can
       output all data generated during a
       run to CSV files in an output directory."""

    def setUp(self) -> None:

        with ConfigFileParser("tests/systemtests/st23/config.json") as cfp:
            self.c = cfp

        self.bds = BatchDataStore()
        self.domain = Domain(self.c)
        self.output_dir = "tests/systemtests/st23/data"
        self.edr = EddyDiffusionRun(self.c, self.output_dir)

    def tearDown(self) -> None:
        for element in listdir(self.output_dir):
            if not element.endswith(".gitkeep"):
                path = join(self.output_dir, element)
                try:
                    shutil.rmtree(path)
                except WindowsError:
                    remove(path)

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
