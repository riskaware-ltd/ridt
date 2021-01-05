import unittest
import json
import os

from ridt.config import RIDTConfig
from ridt.base import ConsistencyError


class TestConsistencyChecker(unittest.TestCase):


    def setUp(self) -> None:

        """setUp method which instantiates the
        :class:`~.RIDTConfig` class."""

        this_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(this_dir, "../../default/config.json")
        with open(path) as f:
            loaded_json = json.load(f)

        self.config = RIDTConfig(loaded_json)


if __name__ == "__main__":
    unittest.main()
