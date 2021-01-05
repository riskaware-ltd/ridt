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


class ST20(unittest.TestCase):

    """System Test 20. Test the system can
       produce contour plots of data where requested. """

    def setUp(self) -> None:

        this_dir = os.path.dirname(os.path.abspath(__file__))
        with ConfigFileParser(join(this_dir, "st20/config.json")) as cfp:
            self.c = cfp

        self.bds = BatchDataStore()
        self.domain = Domain(self.c)
        self.output_dir = join(this_dir, "st20/plots")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.edr = EddyDiffusionRun(self.c, self.output_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.output_dir)

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
