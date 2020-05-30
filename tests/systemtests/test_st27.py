import unittest
from os import listdir
from os.path import join
from os import remove
from os import system
import shutil
import json

from config import ConfigFileParser

from config.ridtconfig import FixedDurationSource
from config.ridtconfig import InstantaneousSource
from config.ridtconfig import InfiniteDurationSource


class ST27(unittest.TestCase):
    """System Test 27. Test the system can
       provide access to all functionality
       via a command line interface."""

    def setUp(self) -> None:
        self.config_path = "tests\systemtests\st27\config.json"
        self.csv_path = "tests\systemtests\st27\csv_to_config.csv"

        self.output_dir = "tests\systemtests\st27\data"
        self.virtualenv_path = ".venv"

    def tearDown(self) -> None:
        for element in listdir(self.output_dir):
            if not element.endswith(".gitkeep"):
                path = join(self.output_dir, element)
                try:
                    shutil.rmtree(path)
                except WindowsError:
                    remove(path)

        with open(self.config_path) as f:
            config = json.load(f)

        csv_config = config
        with open(self.config_path, "w") as w:
            json.dump(csv_config, w)
        w.close()

    def test_run(self):
        try:
            system(f"{self.virtualenv_path}\Scripts\\activate")
            system(f"ridt run {self.config_path} {self.output_dir}")

            output = False
            if listdir(self.output_dir):
                output = True

            self.assertEqual(True, output)

        except Exception:
            print("ridt failure")
            self.assertEqual(True, False)

    def test_csv_to_config(self):
        try:
            modes = ["instantaneous", "infinite_duration", "fixed_duration"]

            ins = {"x": 1.0, "y": 1.0, "z": 1.0, "mass": 1.0, "time": 1.0}
            inf = {"x": 1.0, "y": 1.0, "z": 1.0, "rate": 1.0, "time": 1.0}
            fix = {"x": 1.0, "y": 1.0, "z": 1.0, "rate": 1.0, "start_time": 1.0, "end_time": 2.0}

            system(f"{self.virtualenv_path}\Scripts\\activate")
            system(f"ridt csv-to-config {self.config_path} {self.csv_path}")

            config = ConfigFileParser("tests/systemtests/st27/new_config.json")
            for mode in modes:
                m = getattr(config.modes, mode)
                for source in m.sources.values():
                    if isinstance(source, InstantaneousSource):
                        self.assertEqual(source.__source__, ins)
                    if isinstance(source, InfiniteDurationSource):
                        self.assertEqual(source.__source__, inf)
                    if isinstance(source, FixedDurationSource):
                        self.assertEqual(source.__source__, fix)
        except Exception:
            print("csv_to_config failure")
            self.assertEqual(True, False)


if __name__ == "__main__":
    unittest.main()
