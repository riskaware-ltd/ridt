import unittest
import json
import os

import numpy as np

from data import DataStoreWriter
from data import DataStore

from config import IDMFConfig


class TestDataStoreWriter(unittest.TestCase):

    """Unit tests for the :class:`~.TestDataStoreWriter` class."""

    def setUp(self) -> None:

        """setUp method which creates a dummy data :obj:`dict`
        which is used within the tests. Additionally it
        instantiates the :class:`~.ConfigFileWriter` class."""

        self.out_dir = "tests/unittests/test_resources/datastorewriter"
        self.point_name = "point"
        self.line_name = "line"
        self.plane_name = "plane"

        with open("default/config.json") as f:
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

        self.ds.add_point_data(self.point_name, self.point_data)
        self.ds.add_line_data(self.line_name, self.line_data)
        self.ds.add_plane_data(self.plane_name, self.plane_data)
        self.ds.add_domain_data(self.domain_data)
        DataStoreWriter(self.config, self.ds, self.out_dir)
        self.list_dir = os.listdir(self.out_dir)

    def tearDown(self) -> None:
        for item in self.list_dir:
            path = os.path.join(self.out_dir, item)
            os.remove(path)

    def test_data_store_writer(self):
        self.assertIn(f"{self.point_name}.npy", self.list_dir)
        self.assertIn(f"{self.line_name}.npy", self.list_dir)
        self.assertIn(f"{self.plane_name}.npy", self.list_dir)
