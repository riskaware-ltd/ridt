from config.configfileparser import ConfigFileParser
from config.idmfconfig import IDMFConfig

import numpy as np
from numpy import ndarray


class EddyDiffusion:

    def __init__(self, settings: IDMFConfig):
        self.settings = settings
        self.dim = self.settings.models.eddy_diffusion.dimensions
        self.volume = self.dim.x * self.dim.y * self.dim.z
        self.tkeb_value = self.__coeff()

    def __call__(self, x: float, y: float,  z: float, t: float):
        try:
            return getattr(self, f"_{self.settings.release_type}")(x, y, z, t)
        except AttributeError as e:
            f"Release type must be instantaneous, fixed_duration or infinite_duration"

    def _instantaneous(self, xx, yy, zz, tt):
        sources = self.settings.modes.instantaneous.sources
        concentration = []
        for source_name, source in sources.items():
            print(source)
            r_x = self.__exp(xx, tt, self.dim.x, source.x, source.time)
            r_y = self.__exp(yy, tt, self.dim.y, source.y, source.time)
            r_z = self.__exp(zz, tt, self.dim.z, source.z, source.time)
            concentration.append(self.__instantaneous_concentration(source.mass, tt, r_x, r_y, r_z))
        return sum(concentration)

    def __instantaneous_concentration( self, mass: float, time: float, r_x: float, r_y: float, r_z: float):
        fa_rate = self.settings.fresh_air_change_rate
        return (mass * np.exp(-(fa_rate / self.volume) * time) / (8 * np.power(np.pi * self.tkeb_value * time, 3/2))) * r_x * r_y * r_z

    def __infinite(self, x, y, z, t, n):
        return float
    
    def __fixed(self, x, y, z, t, n):
        return float

    def __exp(self,
              pos: float,
              t: float,
              dimension: float,
              source_pos: float,
              source_time: float):

        image_num = self.settings.models.eddy_diffusion.images.quantity

        rv = []
        print(source_pos)
        for n in range(-image_num, image_num + 1):
            rv.append(
                np.exp((-np.power(pos + 2 * n * dimension - source_pos, 2)) / 4 * self.tkeb_value * t) +
                np.exp((-np.power(pos + 2 * n * dimension + source_pos, 2)) / 4 * self.tkeb_value * t)
            )
        return sum(rv)

    def __coeff(self):
        coeff = self.settings.models.eddy_diffusion.coefficient
        if coeff.calculation == "EXPLICIT":
            return coeff.value
        if coeff.calculation == "TKEB":
            return self.__tkeb()

    def __tkeb(self):
        vent_number = self.settings\
            .models\
            .eddy_diffusion\
            .coefficient\
            .tkeb\
            .number_of_supply_vents

        tkeb_term = self.settings.total_air_change_rate /\
            np.power(self.volume * np.power(vent_number, 2), 1/3)

        upper_pi = 0.827 * tkeb_term + 0.0565
        regression = 0.824 * tkeb_term
        lower_pi = max(0.822 * tkeb_term - 0.0565, 0.001)

        # TODO ASK DSTL about which or all coeffs to evaulate.
        return regression
