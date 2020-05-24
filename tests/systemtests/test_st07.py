import unittest

from config import ConfigFileParser
from config.idmfconfig import ConsistencyError


class ST07(unittest.TestCase):

    """System Test 07. Test that the system can
       parse specified concentration and exposure
       threshold levels from the JSON file."""

    def setUp(self) -> None:

        """setUp method that instantiates the
        :class:`~.IDMFConfig` class."""

        with ConfigFileParser("default/config.json") as cfp:
            self.c = cfp

    def test_verify(self):

        """Verify that :class:`~.Thresholds` class contains
        the threshold attributes."""

        self.assertEqual(
            hasattr(self.c, "thresholds"), True
        )
        self.assertEqual(
            hasattr(self.c.thresholds, "concentration"), True
        )
        self.assertEqual(
            hasattr(self.c.thresholds, "exposure"), True
        )

    def test_thresholds(self):

        """Checks to see if the :class:`~.ConsistencyError` error
        triggers when the number of thresholds exceeds 5."""

        for i in range(6):
            self.c.thresholds.concentration.append(1)
        self.assertRaises(ConsistencyError, self.c.consistency_check)

        for i in range(6):
            self.c.thresholds.exposure.append(1)
        self.assertRaises(ConsistencyError, self.c.consistency_check)


if __name__ == "__main__":
    unittest.main()
