import unittest
from os import listdir
from os.path import join
from os import remove
import shutil

from config import ConfigFileParser

from container import Domain
from container.eddydiffusionrun import EddyDiffusionRun

from data import BatchDataStore
from data import DataStoreReader


class ST25(unittest.TestCase):

    """System Test 25. Test the system
       is able to output the data store
       created during a batch run or
       single run mode to disk."""

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_verify(self):
        pass


if __name__ == "__main__":
    unittest.main()
