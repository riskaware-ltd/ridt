import unittest
import os
import time

from data import DirectoryAgent


class TestDirectoryAgent(unittest.TestCase):

    """Unit tests for the :class:`~.TestDirectoryAgent` class."""

    def setUp(self) -> None:

        """setUp method which creates a dummy data :obj:`dict`
        which is used within the tests. Additionally it
        instantiates the :class:`~.DirectoryAgent` class."""

        self.data = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
        self.outdir = "tests/unittests/test_resources/directoryagent"
        self.run_index = 3
        self.shape = (5, 5)
        self.da = DirectoryAgent(self.outdir, self.shape)
