import sys

from typing import List
from typing import Dict
from typing import Union

from numpy import ndarray
from numpy import any
from numpy import where
from numpy import max
from numpy import argmax
from numpy import unravel_index
from numpy import std
from numpy import mean
from numpy import sqrt

from config import IDMFConfig

from container import Domain

from equation import EddyDiffusion

from data import DataStore

from .exposure import Exposure

from .resultcontainers import Maximum
from .resultcontainers import Exceedance
from .resultcontainers import PercentExceedance
from .resultcontainers import MaxPercentExceedance


class DataStoreAnalyser:

    def __init__(self, setting: IDMFConfig, data_store: DataStore, quantity: str):

        self.setting = setting
        self.domain = Domain(self.setting)
        self.thresholds = getattr(self.setting.thresholds, quantity)
        self.data_store = data_store
        self.quantity = quantity

        self.maximum = list()
        self.exceedance = list()
        self.percent_exceedance = list()
        self.max_percent_exceedance = list()

        self.evaluate()

    def evaluate(self):
        p =  self.setting.models.eddy_diffusion.analysis.percentage_exceedance
        for geometry in self.data_store.geometries:
            for id in getattr(self.data_store, geometry):
                index, value = self.data_store.maximum(geometry, id)
                D = (geometry, id, self.quantity)
                self.maximum.append(Maximum(*D, index, value))
        for t in self.thresholds:
            for geometry in self.data_store.geometries:
                for id in getattr(self.data_store, geometry):
                    D = (geometry, id)
                    index = self.data_store.exceeds(*D, t.value)
                    self.exceedance.append(Exceedance(*D, self.quantity, index, t.value))
                    index = self.data_store.percentage_exceeds(*D, t.value, p)
                    self.percent_exceedance.append(PercentExceedance(*D, self.quantity, index, t.value))
                    index, value = self.data_store.percentage_exceeds_max(geometry, id, t.value)
                    self.max_percent_exceedance.append(MaxPercentExceedance(*D, self.quantity, value, index, t.value))
        
    @property
    def evaluate_time_to_well_mixed(self):
        for i in range(self.setting.time_samples):
            d = self.conc_data.domain[i, :, :, :]
            value = std(d) / mean(d)
            if value <= 0.1:
                return self.domain.time[i]
        return None

    @property
    def steady_state_well_mixed_concentration(self):
        pass

    @property
    def characteristic_diffusion_time(self):
        solver = EddyDiffusion(self.setting)
        dim = self.setting.models.eddy_diffusion.dimensions
        l = sqrt(dim.x * dim.y * dim.z)
        return {
            "x": dim.x / solver.diff_coeff,
            "y": dim.y / solver.diff_coeff,
            "z": dim.z / solver.diff_coeff,
            "v": l / solver.diff_coeff
        }
