import numpy as np

from config.idmfconfig import IDMFConfig


class WellMixedRun:

    def __init__(self, settings: IDMFConfig):

        self._settings = settings
        self.__build_parameter_space()
    
    def __build_parameter_space(self):
        self._space = T

    
    @property
    def settings(self):
        return self._settings

    @property
    def space(self):
        return self._space
    
    def evaluate_over_parameter_space(self, function):
        pass
