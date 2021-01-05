import unittest
import os
import shutil

from ridt.base import ComputationalSpace

from ridt.config import ConfigFileParser

from ridt.data.batchdatastore import BatchDataStoreIDError
from ridt.data import BatchDataStore
from ridt.data import BatchDataStoreWriter


class ST12(unittest.TestCase):

    """System Test 12. Test the system
       can write JSON files to disk."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.RIDTConfig` class and the
           :class:`~.ComputationalSpace` class."""

        this_dir = os.path.dirname(os.path.abspath(__file__))
        self.directory = os.path.join(this_dir, "st12")

        with ConfigFileParser(os.path.join(this_dir, "st11/config.json")) as cfp:
            self.c = cfp

        restrict = {"models": "well_mixed"}
        self.space = ComputationalSpace(self.c, restrict)

    def tearDown(self) -> None:

        for element in os.listdir(self.directory):
            if not element.endswith(".gitkeep"):
                path = os.path.join(self.directory, element)
                try:
                    shutil.rmtree(path)
                except WindowsError:
                    os.remove(path)

    def test_verify(self):

        """Verifies that the config.json file is created
        in the correct directory, then removes the created
        files."""

        bds = BatchDataStore()
        for space in self.space.space:
            bds.add_run(space)

        try:
            BatchDataStoreWriter(
                self.c, bds, self.space, self.directory, "concentration")
        except BatchDataStoreIDError as e:
            pass
        self.assertIn(
            "batch_config.json", os.listdir(f"{self.directory}")
        )


if __name__ == "__main__":
    unittest.main()
