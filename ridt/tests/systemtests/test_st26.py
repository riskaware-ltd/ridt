import unittest
import os
from os import listdir
from os.path import join
from os import remove
import shutil
from pathlib import Path

from ridt.config import ConfigFileParser

from ridt.container import Domain
from ridt.container.eddydiffusionrun import EddyDiffusionRun

from ridt.data import BatchDataStore
from ridt.data import DataStoreReader


class ST26(unittest.TestCase):

    """System Test 26. Test the system can
       output all computed quantities specified
       by the user requirements to the output directory."""

    def setUp(self) -> None:

        this_dir = os.path.dirname(os.path.abspath(__file__))
        with ConfigFileParser(join(this_dir, "st26/config.json")) as cfp:
            self.c = cfp

        self.bds = BatchDataStore()
        self.domain = Domain(self.c)
        self.output_dir = join(this_dir, "st26/data")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.edr = EddyDiffusionRun(self.c, self.output_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.output_dir)

    def test_verify(self):
        output_types = ["concentration", "exposure"]
        geometries = ["points", "lines", "planes"]

        plots = ["points_plots", "lines_plots", "planes_plots"]
        plot_output = []
        ed = self.c.models.eddy_diffusion
        for plot in plots:
            output = getattr(ed, plot).output
            plot_output.append(output)

        for output in output_types:
            for idx, geometry in enumerate(geometries):
                if plot_output[idx]:
                    _path = join(self.output_dir, geometry)
                    self.assertIn(output, listdir(_path))


if __name__ == "__main__":
    unittest.main()
