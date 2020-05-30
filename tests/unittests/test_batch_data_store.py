import unittest
import json

from data import BatchDataStore
from data import DataStore

from config import RIDTConfig


class TestBatchDataStore(unittest.TestCase):

    "Unit tests for the :class:`~.BatchDataStore` class."""

    def setUp(self) -> None:

        """setUp method which instantiates the :class:`~.RIDTConfig` class,
        and the :class:`~.BatchDataStore` class."""

        with open("default/config.json") as f:
            loaded_json = json.load(f)

        self.config = RIDTConfig(loaded_json)

        self.bds = BatchDataStore()

    def test_add_run(self):

        """Adds a run to the batch data store then checks
        to make sure the new items match the type of
        the ones added."""

        self.bds.add_run(self.config)
        self.assertEqual(type(self.bds.store), dict)
        for key, val in self.bds.store.items():
            self.assertEqual(type(key), RIDTConfig)
            self.assertEqual(type(val), DataStore)
