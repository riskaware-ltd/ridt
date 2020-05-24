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

    def __call__(self, x: ndarray, y: ndarray,  z: ndarray, t: ndarray):
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

        image_num = self.settings.models.eddy_diffusion.images.quantity

        def image(arg):
            return exp(-power(arg, 2) / (4 * self.diff_coeff * t))

        rv = list()
        for image_index in range(-image_num, image_num + 1):
            value = position + 2 * image_index * bound
            rv.append(image(value - source_loc) + image(value + source_loc))
        return sum(rv)

    def __coeff(self, t: ndarray):
        fa_rate = self.settings.fresh_air_change_rate
        num = exp(-t * fa_rate / self.volume)
        den  = 8 * power(pi * self.diff_coeff * t, 3 / 2)
        return num / den

    def diffusion_coefficient(self):
        vent_number = self.settings\
            .models\
            .eddy_diffusion\
            .coefficient\
            .tkeb\
            .number_of_supply_vents

        coeff = self.settings.models.eddy_diffusion.coefficient
        if coeff.calculation == "EXPLICIT":
            return coeff.value
        else:
            tkeb_term = self.settings.total_air_change_rate /\
                power(self.volume * power(vent_number, 2), 1/3)

            upper_pi = 0.827 * tkeb_term + 0.0565
            regression = 0.824 * tkeb_term
            lower_pi = max(0.822 * tkeb_term - 0.0565, 0.001)

            # TODO ASK DSTL about which or all coeffs to evaulate.
            return regression

    def temp_conc(self):
        return [copy(self.zero) for i in range(self.settings.time_samples)]