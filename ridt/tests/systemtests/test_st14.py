import unittest
import os
import shutil
from pathlib import Path

from ridt.base import ComputationalSpace

from ridt.config import ConfigFileParser

from ridt.data.batchdatastore import BatchDataStoreIDError
from ridt.data import DataStore
from ridt.data import BatchDataStore
from ridt.data import BatchDataStoreWriter

from ridt.analysis import DataStoreAnalyser
from ridt.analysis import BatchDataStoreAnalyser
from ridt.analysis.batchresultswriter import BatchResultsWriter


class ST14(unittest.TestCase):

    """System Test 14. Test the system can
       provide summary output for a given
       configuration file."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.RIDTConfig` class and the
           :class:`~.ComputationalSpace` class."""

        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        self.out_dir = os.path.join(self.this_dir, "st14/run")
        Path(self.out_dir).mkdir(parents=True, exist_ok=True)

        with ConfigFileParser(os.path.join(self.this_dir, "st14/config.json")) as cfp:
            self.c = cfp

        restrict = {"models": "well_mixed"}
        self.space = ComputationalSpace(self.c, restrict)

    def tearDown(self) -> None:
        shutil.rmtree(self.out_dir)

    def test_verify(self):

        """Verifies that the config.json file is created
        in the correct directory, then removes the created
        files."""

        da = DataStore()
        dsa = DataStoreAnalyser(self.c, da, "concentration")

        bds = BatchDataStore()
        bds.add_run(self.c)

        bdsw = BatchResultsWriter(
            self.c, self.space, {self.c: dsa}, self.out_dir, "concentration"
        )

        try:
            bdsw.write()
        except BatchDataStoreIDError as e:
            pass
        self.assertIn(
            "batch_run_summary.txt", os.listdir(f"{self.out_dir}")
        )

        with open(os.path.join(self.this_dir, "st14/run/batch_run_summary.txt")) as f:
            txt = f.read()

        self.assertIn(
            "Computational space dimensions: 1 x",
            txt
        )


if __name__ == "__main__":
    unittest.main()
