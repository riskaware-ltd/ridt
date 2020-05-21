import unittest

from config import IDMFConfig
from config import ConfigFileParser
from config.idmfconfig import ConsistencyError


class ST01(unittest.TestCase):

    """System Test 01. The objective of this test
    is to prove that the system can parse Json files
    from disk and verify their integrity."""

    def setUp(self) -> None:

        """The set up method for system test 01.
        Configures a valid config file and a config
        file with an error in."""

        with ConfigFileParser("default/config.json") as cfp:
            self.c = cfp
        with ConfigFileParser("tests/systemtests/st01/error_config.json") as cfp:
            self.ec = cfp

    def test_parse(self):

        """Checks to see that the consistency check can raise
        an error in a certain circumstance."""

        self.c.consistency_check()
        print("Correct config successfully parsed.")
        with self.assertRaises(ConsistencyError):
            self.ec.consistency_check()
        print("Error correctly captured.")

    def test_verify(self):

        """Verifies that the config file parser outputs a
        :class:`~.IDMFConfig` class."""

        self.assertEqual(
            type(self.c), IDMFConfig
        )


if __name__ == "__main__":
    unittest.main()
