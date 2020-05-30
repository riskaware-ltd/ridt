import unittest
import json

from config import IDMFConfig
from base import ConsistencyError


class TestConsistencyChecker(unittest.TestCase):

    """Unit tests for the :meth:`~.consistency_check` method of
    the :class:`~.IDMFConfig` class."""

    def setUp(self) -> None:

        """setUp method which instantiates the
        :class:`~.IDMFConfig` class."""

        with open("default/config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)


if __name__ == "__main__":
    unittest.main()
