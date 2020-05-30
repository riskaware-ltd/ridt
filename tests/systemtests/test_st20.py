import unittest
from os import listdir
from os.path import join
from os import remove
import shutil

from config import ConfigFileParser

from container import Domain
from container.eddydiffusionrun import EddyDiffusionRun

from data import BatchDataStore


class ST20(unittest.TestCase):

    """System Test 20. Test the system can
       produce contour plots of data where requested. """

    def setUp(self) -> None:

        with ConfigFileParser("tests/systemtests/st20/config.json") as cfp:
            self.c = cfp

        self.bds = BatchDataStore()
        self.domain = Domain(self.c)
        self.output_dir = "tests/systemtests/st20/plots"
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
        num = self.c.models.eddy_diffusion.planes_plots.number
        for output in output_types:
            _path = join(self.output_dir, "planes", output, "plots")
            for name, val in self.c.models.eddy_diffusion.monitor_locations.planes.items():
                for i in range(num):
                    val = i * (self.c.total_time / (num - 1))
                    self.assertIn(f"{name}-{val}0s.png", listdir(_path))


if __name__ == "__main__":
    unittest.main()
