import unittest

import os

from ridt.base import ComputationalSpace
from ridt.config import ConfigFileParser
from ridt.config import RIDTConfig


class ST11(unittest.TestCase):

    """System Test 11. Test the system can convert
       config files with ranges of values into a set of
       config object, each which can be evaluated separately."""

    def setUp(self) -> None:

        """setUp method that instantiates the
           :class:`~.RIDTConfig` class and the
           :class:`~.ComputationalSpace` class."""

        this_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(this_dir, "st11/config.json")
        with ConfigFileParser(path) as cfp:
            self.c = cfp

            restrict = {"models": "well_mixed"}
            self.space = ComputationalSpace(self.c, restrict)

    def test_verify(self):

        settings_list = list()
        for setting in self.space.space:
            if isinstance(setting, RIDTConfig):
                settings_list.append(setting)
        self.assertEqual(len(settings_list) == 9, True)


if __name__ == "__main__":
    unittest.main()
