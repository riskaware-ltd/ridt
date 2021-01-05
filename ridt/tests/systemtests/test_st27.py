import unittest
import os
from os import listdir
from os.path import join
from os import remove
from os import system
import shutil
import json
from pathlib import Path

from ridt.config import ConfigFileParser

from ridt.config.ridtconfig import FixedDurationSource
from ridt.config.ridtconfig import InstantaneousSource
from ridt.config.ridtconfig import InfiniteDurationSource


class ST27(unittest.TestCase):
    """System Test 27. Test the system can
       provide access to all functionality
       via a command line interface."""

    def setUp(self) -> None:

        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = join(self.this_dir, "st27/config.json")
        self.csv_path = join(self.this_dir, "st27/csv_to_config.csv")

        self.output_dir = join(self.this_dir, "st27/data")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.virtualenv_path = ".venv"

    def tearDown(self) -> None:
        shutil.rmtree(self.output_dir)

        with open(self.config_path) as f:
            config = json.load(f)

        csv_config = config
        with open(self.config_path, "w") as w:
            json.dump(csv_config, w)
        w.close()

    def test_run(self):
        try:
            system(f"{self.virtualenv_path}\\Scripts\\activate")
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

            system(f"{self.virtualenv_path}\\Scripts\\activate")
            system(f"ridt csv-to-config {self.config_path} {self.csv_path}")

            config = ConfigFileParser(os.path.join(self.this_dir, "st27/new_config.json"))
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
