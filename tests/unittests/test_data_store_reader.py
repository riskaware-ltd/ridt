import unittest
import json
import os

import numpy as np

from data import DataStoreReader
from data import DataStoreWriter
from data import DataStore

from config import IDMFConfig


class TestDataStoreReader(unittest.TestCase):

    """Unit tests for the :class:`~.TestDataStoreWriter` class."""

    def setUp(self) -> None:

        """setUp method which creates a dummy data :obj:`dict`
        which is used within the tests. Additionally it
        instantiates the :class:`~.ConfigFileWriter` class."""

        self.out_dir = "tests/unittests/test_resources/datastorereader"
        self.point_name = "point_1"
        self.line_name = "line_1"
        self.plane_name = "plane_1"

        with open("tests/unittests/test_resources/test_config.json") as f:
            loaded_json = json.load(f)

        self.config = IDMFConfig(loaded_json)

        self.ds = DataStore()
        self.space = np.linspace(0, 10, 10)

        self.point_data = np.array(self.space)

        self.line_data = np.array(
            [self.space, self.space])

        self.plane_data = np.array(
            [[self.space, self.space], [self.space, self.space]])

        self.domain_data = np.array(
            [[[self.space, self.space], [self.space, self.space]],
             [[self.space, self.space], [self.space, self.space]]]
        )
