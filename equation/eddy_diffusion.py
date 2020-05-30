import warnings

import numpy

from typing import List
from copy import copy

from numpy import ndarray
from numpy import array
from numpy import zeros
from numpy import ones
from numpy import full
from numpy import exp
from numpy import log
from numpy import power
from numpy import pi
from numpy import heaviside
from numpy import maximum
from numpy import where
from numpy import cumsum
from numpy import clip
from numpy import square
from numpy import nanmean
from numpy import true_divide
from scipy.integrate import cumtrapz


from config import ConfigFileParser
from config import RIDTConfig
from config import InstantaneousSource

numpy.seterr(divide='ignore')
numpy.seterr(invalid='ignore')

class EddyDiffusion:

    def __init__(self, settings: RIDTConfig):
        self.settings = settings
        self.dim = self.settings.dimensions
        self.volume = self.dim.x * self.dim.y * self.dim.z
        self.cumtrapz_kwargs = {
            "axis": 0,
            "initial": 0,
            "dx": self.settings.total_time / self.settings.time_samples
        }
        self.diff_coeff = self.diffusion_coefficient()

    def __call__(self, x: ndarray, y: ndarray,  z: ndarray, t: List[float]):
        modes = ["instantaneous", "infinite_duration", "fixed_duration"]
        self.shape = x.shape
        self.rv = array(self.zero_conc())
        for mode in modes:
            self.sources = getattr(self.settings.modes, mode).sources
            getattr(self, f"{mode}")(x, y, z, t)
        return self.rv

    def instantaneous(self, x: ndarray, y: ndarray, z: ndarray, t: List[float]): 
        for source in self.sources.values():
            conc = self.zero_conc()
            for idx, time in enumerate(t):
                if time - source.time > 0:
                    conc[idx] += source.mass * self.conc(
                        source, x, y, z, time - source.time)
            self.rv += array(conc)

    def infinite_duration(self, x: ndarray, y: ndarray, z: ndarray, t: List[float]):
        for source in self.sources.values():
            conc = self.zero_conc()
            for idx, time in enumerate(t):
                if time - source.time > 0:
                    conc[idx] += source.rate * self.conc(
                        source, x, y, z, time - source.time)
            self.rv += cumtrapz(array(conc), **self.cumtrapz_kwargs)
    
    def fixed_duration(self, x: ndarray, y: ndarray, z: ndarray, t: List[float]):
        for source in self.sources.values():
            conc = self.zero_conc()
            conc_decay = self.zero_conc()
            for idx, time in enumerate(t):
                if time - source.start_time > 0:
                    conc[idx] += source.rate * self.conc(
                        source, x, y, z, time - source.start_time)
                if time - source.start_time - source.end_time > 0:
                    conc_decay[idx] += source.rate * self.conc(
                        source, x, y, z, time - source.end_time)
            arr = array(conc)
            arr_decay = array(conc_decay)
            conc = cumtrapz(arr, **self.cumtrapz_kwargs)
            conc_decay = cumtrapz(arr_decay, **self.cumtrapz_kwargs)
            self.rv += conc - conc_decay
    
    def conc(self,
             source: InstantaneousSource,
             x: ndarray,
             y: ndarray,
             z: ndarray,
             t: float):

        r_x = self.exp(x, t, self.dim.x, source.x)
        r_y = self.exp(y, t, self.dim.y, source.y)
        r_z = self.exp(z, t, self.dim.z, source.z)
        
        return self.coefficient(t) * r_x * r_y * r_z

    def exp(self, position: ndarray, t: float, bound: float, source_loc: float):

        i_setting = self.settings.models.eddy_diffusion.images

        def image(arg):
            return exp(-power(arg, 2) / (4 * self.diff_coeff * t))
        
        def term(position, image_index, bound, source_loc):
            value = position + 2 * image_index * bound
            return image(value - source_loc) + image(value + source_loc)

        rv = zeros(self.shape)
        image_index = 0
        rv += term(position, image_index, bound, source_loc)
        if i_setting.mode == "manual":
            if i_setting.quantity:
                image_index = i_setting.quantity
                for idx in range(1, image_index + 1):
                    rv += term(position, idx, bound, source_loc)
                    rv += term(position, -idx, bound, source_loc)
        else:
            while image_index < 21:
                image_index += 1
                new_term = zeros(self.shape)
                for idx in [image_index, -image_index]:
                    new_term += term(position, idx, bound, source_loc)
                if self.geometric_variance(rv, rv + new_term) < 1 + 1e-10:
                    rv += new_term
                    break
                rv += new_term
        return rv
    
    def geometric_variance(self, old: ndarray, new: ndarray):
        return exp(nanmean(square(log(old)-log(new))))

    def coefficient(self, t: ndarray):
        fa_rate = self.settings.fresh_air_change_rate
        num = exp(-t * fa_rate / self.volume)
        den  = 8 * power(pi * self.diff_coeff * t, 3 / 2)
        return num / den

    def diffusion_coefficient(self):
        tkeb_settings = self.settings.models.eddy_diffusion.coefficient.tkeb
        vent_number = tkeb_settings.number_of_supply_vents
        air_change_rate = tkeb_settings.total_air_change_rate
        coeff = self.settings.models.eddy_diffusion.coefficient
        bound = tkeb_settings.bound

        if coeff.calculation == "EXPLICIT":
            return coeff.value
        else:
            tkeb_term = air_change_rate /\
                power(self.volume * power(vent_number, 2), 1/3)
            if bound == "lower":
                return 0.827 * tkeb_term + 0.0565
            elif bound == "regression":
                return 0.824 * tkeb_term
            elif bound == "upper": 
                return max(0.822 * tkeb_term - 0.0565, 0.001)

    def zero_conc(self):
        return [zeros(self.shape) for i in range(self.settings.time_samples)]
