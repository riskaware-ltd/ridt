import unittest
from os import listdir
from os.path import join
from os import remove
import shutil

from config import ConfigFileParser

from container import Domain
from container.eddydiffusionrun import EddyDiffusionRun

from data import BatchDataStore


class ST24(unittest.TestCase):

    """System Test 24. Test the system
       is able to output the data store
       created during a batch run or
       single run mode to disk."""

    def setUp(self) -> None:

        with ConfigFileParser("tests/systemtests/st23/config.json") as cfp:
            self.c = cfp

        self.bds = BatchDataStore()
        self.domain = Domain(self.c)
        self.output_dir = "tests/systemtests/st23/data"
        self.edr = EddyDiffusionRun(self.c, self.output_dir)

    def tearDown(self) -> None:
        for element in listdir(self.output_dir):
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
                    self.assertIn(f"{name}.npy", listdir(_path))


if __name__ == "__main__":
    unittest.main()
