import unittest
import os
import shutil

from ridt.config.csvtoconfigfile import CSVToConfigFile


class ST13(unittest.TestCase):

    """System Test 13. Test the system is able to take
       CSV files of data defining sources/monitor points
       and convert them into JSON configuration files."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.RIDTConfig` class and the
           :class:`~.ComputationalSpace` class."""

        self.config_file = "tests/systemtests/st13/config.json"
        self.csv_file = "tests/systemtests/st13/info.csv"
        self.output = "tests/systemtests/st13"

    def test_modes(self):
        pass


if __name__ == "__main__":
    unittest.main()
