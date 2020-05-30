import unittest
from os import listdir
from os.path import join
from os import remove
import shutil

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

        with ConfigFileParser("tests/systemtests/st26/config.json") as cfp:
            self.c = cfp

        self.bds = BatchDataStore()
        self.domain = Domain(self.c)
        self.output_dir = "tests/systemtests/st26/data"
        self.edr = EddyDiffusionRun(self.c, self.output_dir)

    def tearDown(self) -> None:
        for element in listdir(self.output_dir):
            if not element.endswith(".gitkeep"):
                path = join(self.output_dir, element)
                try:
                    shutil.rmtree(path)
                except WindowsError:
                    remove(path)

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
