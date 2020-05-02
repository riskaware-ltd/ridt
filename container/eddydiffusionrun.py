from numpy import zeros
from numpy import meshgrid
from numpy import linspace

from config.idmfconfig import IDMFConfig
from base.settings import ComputationalSpace


class EddyDiffusionRun:

    def __init__(self, settings: IDMFConfig):

        self._settings = settings
        self.build_parameter_space()
        self.prepare()
    
    def build_parameter_space(self):
        self._time = linspace(0.0,
                              self.settings.total_time,
                              self.settings.time_samples)
        dim = self.settings.models.eddy_diffusion.dimensions
        sam = self.settings.models.eddy_diffusion.spatial_samples
        self._x = linspace(0.0, dim.x, sam.x)
        self._y = linspace(0.0, dim.y, sam.y)
        self._z = linspace(0.0, dim.z, sam.z)
        self._X, self._Y, self._Z = meshgrid(self._x,
                                             self._y,
                                             self._z,
                                             indexing='ij')
        self._space = (sam.x, sam.y, sam.z, self.settings.time_samples)

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

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z
