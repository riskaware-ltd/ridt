import unittest

import numpy as np

from ridt.data.datastore import DataStore

from ridt.data.datastore import DataStoreDimensionalityError
from ridt.data.datastore import DataStoreTypeError
from ridt.data.datastore import DataStoreIDError


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
