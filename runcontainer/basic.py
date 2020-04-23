import numpy as np

from config.idmfconfig import IDMFConfig


class Basic:

    def __init__(self, settings: IDMFConfig):

        self.settings = settings
        self.__build_parameter_space()
    
    def __build_parameter_space(self):
        self._X, self._Y, self._Z, self._T = np.meshgrid(X, Y, Z, T, indexing='ij')
    
    @property
    def space(self):
        return self._X, self._Y, self._Z, self._T
    
    def evaluate_over_parameter_space(self, function):
        pass

