from numpy import zeros
from numpy import meshgrid
from numpy import linspace

from config.idmfconfig import IDMFConfig
from base.settings import ComputationalSpace


class WellMixedRun:

    def __init__(self, settings: IDMFConfig):

        self._settings = settings
        self.prepare()
        self.build_parameter_space()
    
    def build_parameter_space(self):
        self._time= linspace(0.0,
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
    def time(self):
        return self._time
