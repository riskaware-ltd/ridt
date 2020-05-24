import unittest
import os
import shutil

from config.csvtoconfigfile import CSVToConfigFile


class ST13(unittest.TestCase):

    """System Test 13. Test the system is able to take
       CSV files of data defining sources/monitor points
       and convert them into JSON configuration files."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.IDMFConfig` class and the
           :class:`~.ComputationalSpace` class."""

        config_file = "tests/systemtests/st13/config.json"
        csv_file = "tests/systemtests/st13/info.csv"
        output = "tests/systemtests/st13"

        # with CSVToConfigFile() as ctc:
        #     ctc(config_file, csv_file, output)

    def test_verify(self):
        pass


if __name__ == "__main__":
    unittest.main()
