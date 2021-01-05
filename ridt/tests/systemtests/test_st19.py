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


class ST19(unittest.TestCase):

    """System Test 19. test the system can
       produce line plots of data where requested."""

    def setUp(self) -> None:

        this_dir = os.path.dirname(os.path.abspath(__file__))
        with ConfigFileParser(os.path.join(this_dir, "st19/config.json")) as cfp:
            self.c = cfp

        self.bds = BatchDataStore()
        self.domain = Domain(self.c)
        self.output_dir = os.path.join(this_dir, "st19/plots")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.edr = EddyDiffusionRun(self.c, self.output_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.output_dir)

    def test_verify(self):
        output_types = ["concentration", "exposure"]
        for output in output_types:
            _path = join(self.output_dir, "points", output, "plots")
            for idx, img in enumerate(listdir(_path)):
                self.assertEqual(img, f"point_{idx + 1}.png")


if __name__ == "__main__":
    unittest.main()
