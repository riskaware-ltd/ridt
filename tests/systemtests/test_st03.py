import unittest

from config import ConfigFileParser
from config.idmfconfig import ConsistencyError


class ST03(unittest.TestCase):

    """System Test 03. Test that the system is
    able to parse instantaneous/infinite duration/fixed
    duration sources from the JSON config file.."""

    def setUp(self) -> None:

        """setUp method which instantiates an
        :class:`~.IDMFConfig` class."""

        with ConfigFileParser("default/config.json") as cfp:
            self.c = cfp

    def test_verify(self):

        """Verifies that the :class:`~.IDMFConfig` class
        has the correct source attributes."""

        self.assertEqual(
            hasattr(self.c, "modes"), True)
        self.assertEqual(
            hasattr(self.c.modes, "instantaneous"), True)
        self.assertEqual(
            hasattr(self.c.modes, "infinite_duration"), True)
        self.assertEqual(
            hasattr(self.c.modes, "fixed_duration"), True)

    def test_instantaneous(self):

        """Verify that the :class:`~.InstantaneousSource`
        class has the correct attributes."""

        self.assertEqual(
            hasattr(self.c.modes.instantaneous, "sources"), True)
        for sources in self.c.modes.instantaneous.sources.values():
            self.assertEqual(hasattr(sources, "x"), True)
            self.assertEqual(hasattr(sources, "y"), True)
            self.assertEqual(hasattr(sources, "z"), True)
            self.assertEqual(hasattr(sources, "mass"), True)
            self.assertEqual(hasattr(sources, "time"), True)

    def test_infinite_duration(self):

        """Verify that the :class:`~.InfiniteDuration`
        class has the correct attributes."""

        self.assertEqual(
            hasattr(self.c.modes.infinite_duration, "sources"), True)
        for sources in self.c.modes.infinite_duration.sources.values():
            self.assertEqual(hasattr(sources, "x"), True)
            self.assertEqual(hasattr(sources, "y"), True)
            self.assertEqual(hasattr(sources, "z"), True)
            self.assertEqual(hasattr(sources, "rate"), True)
            self.assertEqual(hasattr(sources, "time"), True)

    def test_fixed_duration(self):

        """Verify that the :class:`~.FixedDuration`
        class has the correct attributes."""

        self.assertEqual(
            hasattr(self.c.modes.fixed_duration, "sources"), True)
        for sources in self.c.modes.fixed_duration.sources.values():
            self.assertEqual(hasattr(sources, "x"), True)
            self.assertEqual(hasattr(sources, "y"), True)
            self.assertEqual(hasattr(sources, "z"), True)
            self.assertEqual(hasattr(sources, "rate"), True)
            self.assertEqual(hasattr(sources, "start_time"), True)
            self.assertEqual(hasattr(sources, "end_time"), True)

    def test_source_times(self):

        """Checks to see if the :class:`.ConsistencyError` error
        triggers when the time of a source is greater than
        the total time of the simulation."""

        for key, value in self.c.modes.instantaneous.sources.items():
            value.time = self.c.total_time + 1
            self.assertRaises(ConsistencyError, self.c.consistency_check)

        for key, value in self.c.modes.infinite_duration.sources.items():
            value.time = self.c.total_time + 1
            self.assertRaises(ConsistencyError, self.c.consistency_check)

        for key, value in self.c.modes.fixed_duration.sources.items():
            value.start_time = self.c.total_time + 1
            self.assertRaises(ConsistencyError, self.c.consistency_check)

        for key, value in self.c.modes.fixed_duration.sources.items():
            value.start_time = value.end_time + 1
            self.assertRaises(ConsistencyError, self.c.consistency_check)


if __name__ == "__main__":
    unittest.main()
