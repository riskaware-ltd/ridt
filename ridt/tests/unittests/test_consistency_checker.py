import unittest
import json

from ridt.config import RIDTConfig
from ridt.base import ConsistencyError


class TestConsistencyChecker(unittest.TestCase):


    def setUp(self) -> None:

        """setUp method which instantiates the
        :class:`~.RIDTConfig` class."""

        with open("default/config.json") as f:
            loaded_json = json.load(f)

        self.config = RIDTConfig(loaded_json)


if __name__ == "__main__":
    unittest.main()
