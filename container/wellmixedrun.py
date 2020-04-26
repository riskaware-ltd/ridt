import numpy as np

from pprint import pprint

from config.idmfconfig import IDMFConfig
from base.settings import ComputationalSpace


class WellMixedRun:

    def __init__(self, settings: IDMFConfig):

        self._settings = settings
        self.prepare()
        self.build_parameter_space()
    
    def prepare(self):
        getattr(self, f"prepare_{self.settings.release_type}")()

    def build_parameter_space(self):
        self._space = np.linspace(0.0, self.settings.total_time, self.settings.time_samples)
    
    def prepare(self):

        restrict = { 
            "modes": self.settings.release_type,
            "models": self.settings.dispersion_model
        }

        space = ComputationalSpace(self.settings, restrict)
        print(space.shape)
        space.axes
   
    @property
    def settings(self):
        return self._settings

    @property
    def space(self):
        return self._space
    
    def evaluate_over_parameter_space(self, function):
        pass

