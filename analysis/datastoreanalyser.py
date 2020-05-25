import sys

from typing import List
from typing import Dict
from typing import Union

from copy import deepcopy

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
from config import Units

from container import Domain

from equation import EddyDiffusion

from data import DataStore
from data import UncertaintyMask

from .exposure import Exposure

from .resultcontainers import Maximum
from .resultcontainers import Exceedance
from .resultcontainers import PercentExceedance
from .resultcontainers import MaxPercentExceedance


class DataStoreAnalyser:

    def __init__(self, setting: IDMFConfig, data_store: DataStore, quantity: str):

        self.setting = setting
        self.units = Units(setting)
        self.domain = Domain(self.setting)
        self.quantity = quantity
        self.thresholds = self.threshold_converter()
        self.data_store = data_store

        if self.setting.models.eddy_diffusion.analysis.exclude_uncertain_values:
            self.exclude_uncertain_values()

        self.maximum = list()
        self.exceedance = list()
        self.percent_exceedance = list()
        self.max_percent_exceedance = list()

        self.evaluate()

    def threshold_converter(self):
        tld = [t.value for t in getattr(self.setting.thresholds, self.quantity)]
        return getattr(self.units, f"{self.quantity}_converter")(tld)

    def evaluate(self):
        p =  self.setting.models.eddy_diffusion.analysis.percentage_exceedance
        for geometry in self.data_store.geometries:
            for id in getattr(self.data_store, geometry):
                index, value = self.data_store.maximum(geometry, id)
                D = (geometry, id, self.quantity)
                self.maximum.append(Maximum(self.setting, *D, index, value))
        for t in self.thresholds:
            for geometry in self.data_store.geometries:
                for id in getattr(self.data_store, geometry):
                    D = (geometry, id)
                    index = self.data_store.exceeds(*D, t)
                    self.exceedance.append(
                        Exceedance(self.setting, *D, self.quantity, index, t))
                    index = self.data_store.percentage_exceeds(*D, t, p)
                    self.percent_exceedance.append(
                        PercentExceedance(self.setting, *D, self.quantity, index, t, p))
                    index, value = self.data_store.percentage_exceeds_max(geometry, id, t)
                    self.max_percent_exceedance.append(
                        MaxPercentExceedance(self.setting, *D, self.quantity, value, index, t))
    
    def exclude_uncertain_values(self):
        new_data_store = deepcopy(self.data_store)
        um = UncertaintyMask(self.setting)
        for geometry in new_data_store.geometries:
            for id in getattr(new_data_store, geometry):
                data = um.mask(geometry, id, new_data_store.get(geometry, id))
                new_data_store.add(geometry, id, data)
        self.data_store = new_data_store
        
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
