import unittest
import os
from os import listdir
from os.path import join
from os import remove
import shutil

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
        for output in output_types:
            _path = join(self.output_dir, "points", output, "plots")
            for idx, img in enumerate(listdir(_path)):
                self.assertEqual(img, f"point_{idx + 1}.png")


if __name__ == "__main__":
    unittest.main()
