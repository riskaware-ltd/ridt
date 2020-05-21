import unittest
import os
import shutil

from base import ComputationalSpace

from config import ConfigFileParser

from data.batchdatastore import BatchDataStoreIDError
from data import BatchDataStore
from data import BatchDataStoreWriter


class ST12(unittest.TestCase):

    """System Test 12. Test the system
       can write JSON files to disk."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.IDMFConfig` class and the
           :class:`~.ComputationalSpace` class."""

        with ConfigFileParser("tests/systemtests/st11/config.json") as cfp:
            self.c = cfp

        restrict = {"models": self.c.dispersion_model}
        self.space = ComputationalSpace(self.c, restrict)

    def test_verify(self):

        """Verifies that the config.json file is created
        in the correct directory, then removes the created
        files."""

        directory = "tests/systemtests/st12"

        bds = BatchDataStore()
        bdsw = BatchDataStoreWriter(
            self.c, bds, self.space
        )

        try:
            bdsw.write(directory)
        except BatchDataStoreIDError as e:
            pass
        self.assertIn(
            "config.json", os.listdir(f"{directory}/[0, 0]")
        )

        for element in os.listdir(directory):
            path = os.path.join(directory, element)
            try:
                shutil.rmtree(path)
            except WindowsError:
                os.remove(path)


if __name__ == "__main__":
    unittest.main()
