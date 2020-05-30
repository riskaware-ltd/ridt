import unittest
from os import listdir
from os.path import join
from os import remove
import shutil

from config import ConfigFileParser

from container import Domain
from container.eddydiffusionrun import EddyDiffusionRun

from data import BatchDataStore


class ST22(unittest.TestCase):

    """System Test 22. Test the system can
       produce animated contour plots
       where requested."""

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_verify(self):
        pass


if __name__ == "__main__":
    unittest.main()
