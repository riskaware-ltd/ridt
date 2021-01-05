import unittest

import os

from ridt.base import ConsistencyError
from ridt.config import RIDTConfig
from ridt.config import ConfigFileParser
from ridt.config.configfileparser import ConfigFileParserValidationError


class ST01(unittest.TestCase):

    """System Test 01. The objective of this test
    is to prove that the system can parse Json files
    from disk and verify their integrity."""

    def setUp(self) -> None:

        """The set up method for system test 01.
        Configures a valid config file and a config
        file with an error in."""

        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        with ConfigFileParser(os.path.join(self.this_dir, "../../default/config.json")) as cfp:
            self.c = cfp

    def test_parse(self):

        """Checks to see that the consistency check can raise
        an error in a certain circumstance."""

        self.c.consistency_check()
        with self.assertRaises(ConsistencyError):
            ConfigFileParser(os.path.join(self.this_dir, "st01/error_config.json"))

    def test_verify(self):

        """Verifies that the config file parser outputs a
        :class:`~.RIDTConfig` class."""

        self.assertEqual(
            type(self.c), RIDTConfig
        )


if __name__ == "__main__":
    unittest.main()
