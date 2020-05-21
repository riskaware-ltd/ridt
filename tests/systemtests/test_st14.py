import unittest
import os
import shutil

from base import ComputationalSpace

from config import ConfigFileParser

from data.batchdatastore import BatchDataStoreIDError
from data import BatchDataStore
from data import BatchDataStoreWriter


class ST14(unittest.TestCase):

    """System Test 14. Test the system can
       provide summary output for a given
       configuration file."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.IDMFConfig` class and the
           :class:`~.ComputationalSpace` class."""

        with ConfigFileParser("tests/systemtests/st14/config.json") as cfp:
            self.c = cfp

        restrict = {"models": self.c.dispersion_model}
        self.space = ComputationalSpace(self.c, restrict)

    def test_verify(self):

        """Verifies that the config.json file is created
        in the correct directory, then removes the created
        files."""

        directory = "tests/systemtests/st14/run"

        bds = BatchDataStore()
        bdsw = BatchDataStoreWriter(
            self.c, bds, self.space
        )

        try:
            bdsw.write(directory)
        except BatchDataStoreIDError as e:
            pass
        self.assertIn(
            "run_summary.txt", os.listdir(f"{directory}")
        )

        with open("tests/systemtests/st14/run/run_summary.txt") as f:
            txt = f.read()

        self.assertIn(
            "Computational space dimensions: 3 x 3",
            txt
        )
        self.assertIn(
            "values:  [0.01, 0.001, 0.0001]",
            txt
        )
        self.assertIn(
            "models -> eddy_diffusion -> monitor_locations -> planes -> plane_1 -> distance",
            txt
        )
        self.assertIn(
            "values:  [1.0, 2.0, 3.0]",
            txt
        )

        for element in os.listdir(directory):
            path = os.path.join(directory, element)
            try:
                shutil.rmtree(path)
            except WindowsError:
                os.remove(path)


if __name__ == "__main__":
    unittest.main()
