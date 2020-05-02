from numpy import ndarray
from numpy import zeros
from numpy import array 

from config.idmfconfig import IDMFConfig

import numpy as np


class WellMixed:

    def __init__(self, settings: IDMFConfig):
        self.settings = settings
        self.sources = getattr(self.settings.modes, self.settings.release_type).sources
        self.volume = settings.models.well_mixed.volume
        self.fa_rate = settings.fresh_air_change_rate
        self.shape = (self.settings.time_samples,)
        self.conc = zeros(self.shape)

    def __call__(self, t: np.ndarray):
        return getattr(self, f"{self.settings.release_type}")(t)

    def concentration(self, t: float):
        return np.exp(-(self.fa_rate / self.volume) * t)

    def instantaneous(self, t: np.ndarray):
        for idx, time in enumerate(t):
            for source in self.sources.values():
                if time - source.time > 0:
                    self.conc[idx] += (source.mass / self.volume) *\
                        self.concentration(time - source.time)
        return array(self.conc)

    def infinite_duration(self, t: ndarray):
        for idx, time in enumerate(t):
            for source in self.sources.values():
                if time - source.time > 0:
                    self.conc[idx] += (source.rate / self.fa_rate) *\
                        (1 - self.concentration(time - source.time))
        return array(self.conc)

    def fixed_duration(self, t: ndarray):
        end_int = 0
        for idx, time in enumerate(t):
            for source in self.sources.values():
                if time < source.start_time:
                    pass
                elif time < source.end_time:
                    self.conc[idx] += (source.rate / self.fa_rate) *\
                        (1 - self.concentration(time - source.start_time))
                else:
                    if not end_int:
                        end_int = idx - 1
                    self.conc[idx] += self.conc[end_int] * self.concentration(
                        time - source.end_time)
        return array(self.conc)
