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


class ST28(unittest.TestCase):
    """System Test 28. Check that the eddy diffusion model output matches the 
    verification data."""

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

    def loadpoint(self, cat: str, num: int):
        path = join(
            self.root,
            cat,
            "out",
            "points",
            "concentration",
            "data",
            f"point_{num}.npy")
        return load(path)

    def loadline(self, cat: str, num: int):
        path = join(
            self.root,
            cat,
            "out",
            "lines",
            "concentration",
            "data",
            f"line_{num}.npy")
        return load(path)

    def setUp(self) -> None:
        self.root = join(dirname(__file__), "st28")
        self.cat = [
            "insacr0point",
            "insacr0line",
            "insacr5point",
            "insacr5line",
            "infacr0point",
            "infacr0line",
            "infacr5point",
            "infacr5line",
            "fixacr0point",
            "fixacr0line",
            "fixacr5point"
            "fixacr5line"
        ]

    def test_insacr0point(self):
        idstr = "insacr0point"
        print("")
        print(idstr)
        valpoints = self.points(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")
        print(self.out(idstr))

        points = [self.loadpoint(idstr, num) for num in range(1, 4)]
        points = [array([p for i, p in enumerate(point)]) for point in points]
        points = [delete(point, 0) for point in points]

        for idp, point in enumerate(points):
            for idx, item in enumerate(self.percentage_error(point, valpoints[:, idp])):
                self.assertTrue(item < 0.1)
        print("")
        delete_folder_contents(self.out(idstr))

    
    def test_insacr0line(self):
        idstr = "insacr0line"
        print("")
        print(idstr)
        valpoints = self.lines(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        lines = [self.loadline(idstr, num) for num in range(1, 4)]
        lines = [line[-1, :] for line in lines]

        for idp, line in enumerate(lines):
            for idx, item in enumerate(self.percentage_error(line, valpoints[:, idp])):
                self.assertTrue(item < 0.1)
        print("")
        delete_folder_contents(self.out(idstr))
   
    
    def test_insacr5point(self):
        idstr = "insacr5point"
        print("")
        print(idstr)
        valpoints = self.points(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        points = [self.loadpoint(idstr, num) for num in range(1, 4)]
        points = [array([p for i, p in enumerate(point)]) for point in points]
        points = [delete(point, 0) for point in points]

        for idp, point in enumerate(points):
            for idx, item in enumerate(self.percentage_error(point, valpoints[:, idp])):
                self.assertTrue(item < 0.1)
        print("")
        delete_folder_contents(self.out(idstr))

    
    def test_insacr5line(self):
        idstr = "insacr5line"
        print("")
        print(idstr)
        valpoints = self.lines(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        lines = [self.loadline(idstr, num) for num in range(1, 4)]
        lines = [line[-1, :] for line in lines]

        for idp, line in enumerate(lines):
            for idx, item in enumerate(self.percentage_error(line, valpoints[:, idp])):
                self.assertTrue(item < 0.1)
        print("")
        delete_folder_contents(self.out(idstr))


    
    def test_infacr5point(self):
        idstr = "infacr5point"
        print("")
        print(idstr)
        valpoints = self.points(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        points = [self.loadpoint(idstr, num) for num in range(1, 4)]
        points = [array([p for i, p in enumerate(point)]) for point in points]
        points = [delete(point, 0) for point in points]

        for idp, point in enumerate(points):
            for idx, item in enumerate(self.percentage_error(point, valpoints[:, idp])):
                self.assertTrue(item < 0.1)
        print("")
        delete_folder_contents(self.out(idstr))

    
    def test_infacr5line(self):
        idstr = "infacr5line"
        print("")
        print(idstr)
        valpoints = self.lines(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        lines = [self.loadline(idstr, num) for num in range(1, 4)]
        lines = [line[-1, :] for line in lines]

        for idp, line in enumerate(lines):
            for idx, item in enumerate(self.percentage_error(line, valpoints[:, idp])):
                self.assertTrue(item < 0.1)
        delete_folder_contents(self.out(idstr))
    
    
    def test_infacr0point(self):
        idstr = "infacr0point"
        print("")
        print(idstr)
        valpoints = self.points(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        points = [self.loadpoint(idstr, num) for num in range(1, 4)]
        points = [array([p for i, p in enumerate(point)]) for point in points]
        points = [delete(point, 0) for point in points]

        for idp, point in enumerate(points):
            for idx, item in enumerate(self.percentage_error(point, valpoints[:, idp])):
                self.assertTrue(item < 0.1)
        print("")
        delete_folder_contents(self.out(idstr))

    
    def test_infacr0line(self):
        idstr = "infacr0line"
        print("")
        print(idstr)
        valpoints = self.lines(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        lines = [self.loadline(idstr, num) for num in range(1, 4)]
        lines = [line[-1, :] for line in lines]

        for idp, line in enumerate(lines):
            for idx, item in enumerate(self.percentage_error(line, valpoints[:, idp])):
                self.assertTrue(item < 0.1)
        delete_folder_contents(self.out(idstr))

    
    def test_fixacr5point(self):
        idstr = "fixacr5point"
        print("")
        print(idstr)
        valpoints = self.points(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        points = [self.loadpoint(idstr, num) for num in range(1, 4)]
        points = [array([p for i, p in enumerate(point)]) for point in points]
        points = [delete(point, 0) for point in points]

        for idp, point in enumerate(points):
            for idx, item in enumerate(self.percentage_error(point, valpoints[:, idp])):
                self.assertTrue(item < 0.1)
        print("")
        delete_folder_contents(self.out(idstr))
    
    def test_fixacr5line(self):
        idstr = "fixacr5line"
        print("")
        print(idstr)
        valpoints = self.lines(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        lines = [self.loadline(idstr, num) for num in range(1, 4)]
        lines = [line[-1, :] for line in lines]

        for idp, line in enumerate(lines):
            for idx, item in enumerate(self.percentage_error(line, valpoints[:, idp])):
                self.assertTrue(item < 0.1)
        delete_folder_contents(self.out(idstr))
    
    def test_fixacr0point(self):
        idstr = "fixacr0point"
        print("")
        print(idstr)
        valpoints = self.points(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        points = [self.loadpoint(idstr, num) for num in range(1, 4)]
        points = [array([p for i, p in enumerate(point)]) for point in points]
        points = [delete(point, 0) for point in points]

        for idp, point in enumerate(points):
            for idx, item in enumerate(self.percentage_error(point, valpoints[:, idp])):
                self.assertTrue(item < 0.1)
        print("")
        delete_folder_contents(self.out(idstr))

    def test_fixacr0line(self):
        idstr = "fixacr0line"
        print("")
        print(idstr)
        valpoints = self.lines(idstr)

        system(f"ridt run {self.conf(idstr)} {self.out(idstr)}")

        lines = [self.loadline(idstr, num) for num in range(1, 4)]
        lines = [line[-1, :] for line in lines]

        for idp, line in enumerate(lines):
            for idx, item in enumerate(self.percentage_error(line, valpoints[:, idp])):
                self.assertTrue(item < 0.1)
        delete_folder_contents(self.out(idstr))



if __name__ == "__main__":
    unittest.main()