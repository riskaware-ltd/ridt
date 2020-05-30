import unittest
from os import listdir
from os.path import join
from os import remove
import shutil

from ridt.config import ConfigFileParser

from ridt.container import Domain
from ridt.container.eddydiffusionrun import EddyDiffusionRun

from ridt.data import BatchDataStore


class ST21(unittest.TestCase):

    """System Test 21. Test the system can
    produce animated line plots (in time)
    where requested."""

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_verify(self):
        pass


if __name__ == "__main__":
    unittest.main()
