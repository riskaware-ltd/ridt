from numpy import ndarray
from numpy import array
from numpy import zeros
from numpy import ones
from numpy import full
from numpy import exp
from numpy import power
from numpy import pi
from numpy import heaviside
from numpy import maximum
from numpy import where
from numpy import cumsum
from numpy import clip
from numpy import mean
from numpy import true_divide

from typing import List
from copy import copy

from config import ConfigFileParser
from config import IDMFConfig
from config import InstantaneousSource


class EddyDiffusion:

    def __init__(self, settings: IDMFConfig):
        self.settings = settings
        self.dim = self.settings.models.eddy_diffusion.dimensions
        self.volume = self.dim.x * self.dim.y * self.dim.z
        samples = self.settings.models.eddy_diffusion.spatial_samples
        self.delta_t = self.settings.total_time / self.settings.time_samples
        self.diff_coeff = self.diffusion_coefficient()

    def __call__(self, x: ndarray, y: ndarray,  z: ndarray, t: List[float]):
        modes = ["instantaneous", "infinite_duration", "fixed_duration"]
        self.shape = x.shape
        self.zero = zeros(self.shape)
        self.conc = array(self.temp_conc())
        for mode in modes:
            self.sources = getattr(self.settings.modes, mode).sources
            getattr(self, f"{mode}")(x, y, z, t)
        return self.conc

    def instantaneous(self, x: ndarray, y: ndarray, z: ndarray, t: List[float]): 
        for source in self.sources.values():
            temp_conc = self.temp_conc()
            for idx, time in enumerate(t):
                if time - source.time > 0:
                    temp_conc[idx] += source.mass * self.__concentration(
                        source, x, y, z, time - source.time)



            self.conc += array(temp_conc)

    def infinite_duration(self, x: ndarray, y: ndarray, z: ndarray, t: List[float]):
        for source in self.sources.values():
            temp_conc = self.temp_conc()
            for idx, time in enumerate(t):
                if time - source.time > 0:
                    temp_conc[idx] += source.rate * self.__concentration(
                        source, x, y, z, time - source.time)
            self.conc += cumsum(array(temp_conc), axis=0) * self.delta_t
    
    def fixed_duration(self, x: ndarray, y: ndarray, z: ndarray, t: List[float]):
        for source in self.sources.values():
            temp_conc = self.temp_conc()
            temp_conc_decay = self.temp_conc()
            for idx, time in enumerate(t):
                if time - source.start_time > 0:
                    temp_conc[idx] += source.rate * self.__concentration(
                        source, x, y, z, time - source.start_time)
                if time - source.start_time - source.end_time > 0:
                    temp_conc_decay[idx] += source.rate * self.__concentration(
                        source, x, y, z, time - source.end_time)
            temp_conc = cumsum(array(temp_conc), axis=0) * self.delta_t
            temp_conc_decay = cumsum(array(temp_conc_decay), axis=0) * self.delta_t
            self.conc += temp_conc - temp_conc_decay
    
    def __concentration(self,
                        source: InstantaneousSource,
                        x: ndarray,
                        y: ndarray,
                        z: ndarray,
                        t: float):

        r_x = self.__exp(x, t, self.dim.x, source.x)
        r_y = self.__exp(y, t, self.dim.y, source.y)
        r_z = self.__exp(z, t, self.dim.z, source.z)
        
        return self.__coeff(t) * r_x * r_y * r_z

    def __exp(self, position: ndarray, t: float, bound: float, source_loc: float):

        i_setting = self.settings.models.eddy_diffusion.images

        def image(arg):
            return exp(-power(arg, 2) / (4 * self.diff_coeff * t))
        
        def term(position, image_index, bound, source_loc):
            value = position + 2 * image_index * bound
            return image(value - source_loc) + image(value + source_loc)

        rv = zeros(self.shape)
        if i_setting.mode == "manual":
            image_index = 0
            rv += term(position, image_index, bound, source_loc)
            if i_setting.quantity:
                image_index = i_setting.quantity
                for idx in range(1, image_index + 1):
                    rv += term(position, idx, bound, source_loc)
                    rv += term(position, idx, bound, source_loc)
        else:
            while True:
                new_term = zeros(self.shape)
                for idx in [image_index, -image_index]:
                    new_term += term(position, idx, bound, source_loc)
                if mean(100 * true_divide(new_term, rv, where=(new_term!=0) | (rv!=0))) < i_setting.max_error:
                    break
                else:
                    rv += new_term
                image_index += 1
                
        return rv

    def __coeff(self, t: ndarray):
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

    def temp_conc(self):
        return [copy(self.zero) for i in range(self.settings.time_samples)]
