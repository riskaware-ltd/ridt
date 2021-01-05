import unittest
import json
import os

from ridt.data import BatchDataStore
from ridt.data import DataStore

from ridt.config import RIDTConfig


class TestBatchDataStore(unittest.TestCase):

    "Unit tests for the :class:`~.BatchDataStore` class."""

    def setUp(self) -> None:

        """setUp method which instantiates the :class:`~.RIDTConfig` class,
        and the :class:`~.BatchDataStore` class."""

        this_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(this_dir, "../../default/config.json")
        with open(path) as f:
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
