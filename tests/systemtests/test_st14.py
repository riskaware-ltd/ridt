import unittest
import os
import shutil

from base import ComputationalSpace

from config import ConfigFileParser

from data.batchdatastore import BatchDataStoreIDError
from data import DataStore
from data import BatchDataStore
from data import BatchDataStoreWriter

from analysis import DataStoreAnalyser
from analysis import BatchDataStoreAnalyser
from analysis.batchresultswriter import BatchResultsWriter


class ST14(unittest.TestCase):

    """System Test 14. Test the system can
       provide summary output for a given
       configuration file."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.RIDTConfig` class and the
           :class:`~.ComputationalSpace` class."""

        self.out_dir = "tests/systemtests/st14/run"

        with ConfigFileParser("tests/systemtests/st14/config.json") as cfp:
            self.c = cfp

        restrict = {"models": "well_mixed"}
        self.space = ComputationalSpace(self.c, restrict)

    def tearDown(self) -> None:
        for element in os.listdir(self.out_dir):
            if not element.endswith(".gitkeep"):
                path = os.path.join(self.out_dir, element)
                try:
                    shutil.rmtree(path)
                except WindowsError:
                    os.remove(path)

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

        with open("tests/systemtests/st14/run/batch_run_summary.txt") as f:
            txt = f.read()

        self.assertIn(
            "Computational space dimensions: 1 x",
            txt
        )


if __name__ == "__main__":
    unittest.main()
