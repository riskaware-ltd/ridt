from numpy import zeros
from numpy import meshgrid
from numpy import linspace

from config.idmfconfig import IDMFConfig
from base.settings import ComputationalSpace

#################### Review imports before implementation
from equation import WellMixed
from analysis import PointPlot


class WellMixedRun:

    def __init__(self, settings: IDMFConfig, output_dir: str):
        self._settings = settings
        self._output_dir = output_dir
        self.build_parameter_space()
        self.run(settings)
        # self.prepare()

    def build_parameter_space(self):
        self._time = linspace(0.0,
                              self.settings.total_time,
                              self.settings.time_samples)
        self._space = (self.settings.time_samples)

    def prepare(self):
        restrict = {
            "modes": self.settings.release_type,
            "models": self.settings.dispersion_model
        }

        space = ComputationalSpace(self.settings, restrict)
        data = zeros(shape=(*space.shape, *self._space))

    @property
    def settings(self):
        return self._settings

    @property
    def output_dir(self):
        return self._output_dir

    @property
    def time(self):
        return self._time

    ############################## To be reviewed before implementation
    def run(self, settings: IDMFConfig):
        wm = WellMixed(settings)
        conc = wm(self.time)
        pp = PointPlot(settings, self.output_dir)
        pp(conc)
