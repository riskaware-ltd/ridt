import unittest
import os
from os import listdir
from os.path import join
from os import remove
from pathlib import Path

import shutil

from ridt.config import ConfigFileParser

from ridt.container import Domain
from ridt.container.eddydiffusionrun import EddyDiffusionRun

from ridt.data import BatchDataStore
from ridt.data import BatchDataStoreWriter


class ST18(unittest.TestCase):

    """System Test 18. test the system can
       write all data output by the models to
       a given directory."""

    def setUp(self) -> None:

        this_dir = os.path.dirname(os.path.abspath(__file__))
        with ConfigFileParser(os.path.join(this_dir, "st16/explicit.json")) as cfp:
            self.c = cfp

        self.bds = BatchDataStore()
        self.domain = Domain(self.c)
        self.output_dir = os.path.join(this_dir, "st18")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.edr = EddyDiffusionRun(self.c, self.output_dir)
        self.list_dir = listdir(self.output_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.output_dir)

    def test_write(self):

        geometries = ["points", "lines", "planes"]
        output_types = ["concentration", "exposure"]

        for geometry in geometries:
            for output in output_types:
                _dir = f"{geometry}/{output}/data"
                _path = join(self.output_dir, _dir)
                for val in self.edr.data_store.store.values():
                    for name, monitor in getattr(val, geometry).items():
                        self.assertIn(f"{name}.npy", listdir(_path))
                        self.assertIn(f"{name}.csv", listdir(_path))


if __name__ == "__main__":
    unittest.main()
