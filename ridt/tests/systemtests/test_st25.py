import unittest
from os import listdir
from os.path import join
from os import remove
import shutil

from ridt.config import ConfigFileParser

from ridt.container import Domain
from ridt.container.eddydiffusionrun import EddyDiffusionRun

from ridt.data import BatchDataStore
from ridt.data import DataStoreReader


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
