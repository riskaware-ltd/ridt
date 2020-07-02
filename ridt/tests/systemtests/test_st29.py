import unittest
import shutil

from os.path import join
from os.path import dirname
from os.path import isfile
from os.path import isdir
from os.path import islink
from os import listdir
from os import system
from os import unlink

from numpy import genfromtxt
from numpy import load
from numpy import delete
from numpy import ndarray
from numpy import array
from numpy import abs

from ridt.config import ConfigFileParser

from ridt.config.ridtconfig import FixedDurationSource
from ridt.config.ridtconfig import InstantaneousSource
from ridt.config.ridtconfig import InfiniteDurationSource

def delete_folder_contents(path: str):
    for filename in listdir(path):
        file_path = join(path, filename)
        try:
            if isfile(file_path) or islink(file_path):
                unlink(file_path)
            elif isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

class ST27(unittest.TestCase):
    """System Test 28. Check output against verification data."""
    def conf(self, cat: str):
        return join(self.root, cat, "config.json")
    
    def out(self, cat: str):
        return join(self.root, cat, "out")
    
    def points(self, cat: str):
        path = join(self.root, cat, "points.csv")
        with open(path, 'r', encoding='utf-8-sig') as f:
            return genfromtxt(f, delimiter=',')
    
    def lines(self, cat: str):
        path = join(self.root, cat, "lines.csv")
        with open(path, 'r', encoding='utf-8-sig') as f:
            return genfromtxt(f, delimiter=',')
    
    def percentage_error(self, test_data: ndarray, val_data: ndarray):
        return abs(((test_data - val_data) / val_data)) * 100

    def loadpoint(self, cat: str):
        path = join(
            self.root,
            cat,
            "out",
            "points",
            "concentration",
            "data",
            f"well_mixed.npy")
        return load(path)

    def setUp(self) -> None:
        self.root = join(dirname(__file__), "st29")
        self.cat = ["ins", "inf", "fix"]

    def tearDown(self) -> None:
        for cat in self.cat:
            delete_folder_contents(self.out(cat))

    def test_ins(self):
        idstr = "ins"
        print("")
        print(idstr)

        valpoints = self.points(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        point = self.loadpoint(idstr)

        for idx, item in enumerate(self.percentage_error(point, valpoints)):
            self.assertTrue(item < 0.1)
        print("")

    def test_inf(self):
        idstr = "inf"
        print("")
        print(idstr)

        valpoints = self.points(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        point = self.loadpoint(idstr)
        point = delete(point, 0)
        valpoints = delete(valpoints, 0)

        for idx, item in enumerate(self.percentage_error(point, valpoints)):
            self.assertTrue(item < 0.1)
        print("")

    def test_fix(self):
        idstr = "fix"
        print("")
        print(idstr)

        valpoints = self.points(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        point = self.loadpoint(idstr)
        point = delete(point, 0)
        valpoints = delete(valpoints, 0)

        for idx, item in enumerate(self.percentage_error(point, valpoints)):
            self.assertTrue(item < 0.1)
        print("")




if __name__ == "__main__":
    unittest.main()
