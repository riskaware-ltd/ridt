import numpy as np

from config.idmfconfig import IDMFConfig


class Basic:

    def __init__(self, settings: IDMFConfig):

        self._settings = settings
        self.__build_parameter_space()
    
    def __build_parameter_space(self):
        if self.settings.dispersion_model is "eddy_diffusion":
            self._space = np.meshgrid(X, Y, Z, T, indexing='ij')
        else:
            self._space = T

    
    @property
    def settings(self):
        return self._settings

    @property
    def space(self):
        return self._space
    
    def evaluate_over_parameter_space(self, function):
        pass
