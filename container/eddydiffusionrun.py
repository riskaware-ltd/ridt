import numpy as np

from config.idmfconfig import IDMFConfig


class EddyDiffusionRun:

    def __init__(self, settings: IDMFConfig):

        self._settings = settings
        self.__build_parameter_space()
    
    def __build_parameter_space(self):
        pass
        # self._space = np.meshgrid(X, Y, Z, T, indexing='ij')
    
    @property
    def settings(self):
        return self._settings

    @property
    def space(self):
        return self._space
    
    def evaluate_over_parameter_space(self, function):
        pass
