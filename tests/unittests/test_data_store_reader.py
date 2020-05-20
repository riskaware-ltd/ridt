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

        self.ds.add_point_data(self.point_name, self.point_data)
        self.ds.add_line_data(self.line_name, self.line_data)
        self.ds.add_plane_data(self.plane_name, self.plane_data)
        self.ds.add_domain_data(self.domain_data)
        DataStoreWriter(self.config, self.ds, self.out_dir)
        self.list_dir = os.listdir(self.out_dir)

    def test_data_store_reader(self):
        rv = DataStoreReader(self.config, self.out_dir)

        point = np.array_equal(rv.points["point_1"], self.point_data)
        line = np.array_equal(rv.lines["line_1"], self.line_data)
        plane = np.array_equal(rv.planes["plane_1"], self.plane_data)

        self.assertEqual(point, True)
        self.assertEqual(line, True)
        self.assertEqual(plane, True)

        for item in self.list_dir:
            path = os.path.join(self.out_dir, item)
            os.remove(path)
