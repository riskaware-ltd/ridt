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
from numpy import nanstd
from numpy import nanmean
from numpy import sqrt

from config import RIDTConfig
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

    def __init__(self, setting: RIDTConfig, data_store: DataStore, quantity: str):

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

    @property
    def geometries(self):
        locations = self.setting.models.eddy_diffusion.monitor_locations
        return [g for g, e in locations.evaluate.items() if e]

    def threshold_converter(self):
        tld = [t.value for t in getattr(self.setting.thresholds, self.quantity)]
        return getattr(self.units, f"{self.quantity}_converter")(tld)

    def evaluate(self):
        p =  self.setting.models.eddy_diffusion.analysis.percentage_exceedance
        for geometry in self.geometries:
            for id in getattr(self.data_store, geometry):
                index, value = self.data_store.maximum(geometry, id)
                D = (geometry, id, self.quantity)
                self.maximum.append(Maximum(self.setting, *D, index, value))
        for t in self.thresholds:
            for geometry in self.geometries:
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
        for geometry in self.geometries:
            for id in getattr(new_data_store, geometry):
                data = um.mask(geometry, id, new_data_store.get(geometry, id))
                new_data_store.add(geometry, id, data)
        self.data_store = new_data_store

    @property
    def time_to_well_mixed(self):
        for i in range(self.setting.time_samples):
            d = self.data_store.domain["domain"][i, :, :, :]
            value = nanstd(d) / nanmean(d)
            if value <= 0.1:
                return self.domain.time[i]
        return None
