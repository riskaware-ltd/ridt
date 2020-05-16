import unittest

import numpy as np

from data import DataStore

from data.datastore import DataStoreDimensionalityError
from data.datastore import DataStoreTypeError
from data.datastore import DataStoreIDError


class TestDataStore(unittest.TestCase):

    """Unit tests for the :class:`~.DataStore` class."""

    def setUp(self) -> None:

        """setUp method which instantiates the :class:`~.DataSore` class,
        and creates all the data for the tests."""

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

    def test_verify(self):

        """Tests the :meth:`~.verify` method and ensures that
        the correct Errors are raised."""

        data_list = [i for i in range(10)]
        dim = 3
        with self.assertRaises(DataStoreTypeError):
            self.ds.verify(data_list, dim)
        with self.assertRaises(DataStoreDimensionalityError):
            self.ds.verify(self.space, dim)

    def test_point_data(self):

        """Tests to make sure that the point which is added
        to the :class:`~.DataStore` class are equal to what
        added initially."""

        id_str = "point_1"
        self.ds.add_point_data(id_str, self.point_data)
        self.assertEqual(len(self.ds.points), 1)
        for key, val in self.ds.points.items():
            self.assertEqual(key, id_str)
            self.assertEqual(True, np.array_equal(self.point_data, val))

        self.assertEqual(
            True, np.array_equal(self.point_data, self.ds.get_point_data(id_str)))

    def test_line_data(self):

        """Tests to make sure that the line which is added
        to the :class:`~.DataStore` class are equal to what
        added initially."""

        id_str = "line_1"
        self.ds.add_line_data(id_str, self.line_data)
        self.assertEqual(len(self.ds.lines), 1)
        for key, val in self.ds.lines.items():
            self.assertEqual(key, id_str)
            self.assertEqual(True, np.array_equal(self.line_data, val))

        self.assertEqual(
            True, np.array_equal(self.line_data, self.ds.get_line_data(id_str)))

    def test_plane_dat(self):

        """Tests to make sure that the plane which is added
        to the :class:`~.DataStore` class are equal to what
        added initially."""

        id_str = "plane_1"
        self.ds.add_plane_data(id_str, self.plane_data)
        self.assertEqual(len(self.ds.planes), 1)
        for key, val in self.ds.planes.items():
            self.assertEqual(key, id_str)
            self.assertEqual(True, np.array_equal(self.plane_data, val))

        self.assertEqual(
            True, np.array_equal(self.plane_data, self.ds.get_plane_data(id_str)))

    def test_add_domain_data(self):

        """Tests to make sure that the domain which is added
        to the :class:`~.DataStore` class are equal to what
        added initially."""

        self.ds.add_domain_data(self.domain_data)
        self.assertEqual(True, np.array_equal(self.domain_data, self.ds.domain))

        self.assertEqual(
            True, np.array_equal(self.domain_data, self.ds.get_domain_data()))
