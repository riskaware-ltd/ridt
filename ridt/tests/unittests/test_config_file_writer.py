import unittest
import json

import numpy as np

from ridt.config import ConfigFileWriter
from ridt.config.configfilewriter import ConfigFileWriterOSError


class TestConfigFileWriter(unittest.TestCase):

    """Unit tests for the :class:`~.ConfigFileWriter` class."""

    def setUp(self) -> None:

        """setUp method which creates a dummy data :obj:`dict`
        which is used within the tests. Additionally it
        instantiates the :class:`~.ConfigFileWriter` class."""

        self.data = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}

    def test_write(self):

        """Tests the write method to ensure that what is written
        into the json matches the given :obj:`dict`"""

        ConfigFileWriter(
            "tests/unittests/test_resources",
            "configfilewritertest.json",
            self.data)

        with open("tests/unittests/test_resources/configfilewritertest.json") as f:
            test_file = json.load(f)
        self.assertEqual(test_file, self.data)

    def test_OSError(self):

        """Ensures that the :class:`~.ConfigFileWriterOSError`
        passes when the file path is incorrect."""

        with self.assertRaises(ConfigFileWriterOSError):
            ConfigFileWriter(
                "tests/test_resource",
                "testfilepath.json",
                self.data)
