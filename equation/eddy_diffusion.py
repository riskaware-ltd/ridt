from numpy import ndarray
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

from config.configfileparser import ConfigFileParser
from config.idmfconfig import IDMFConfig
from config.idmfconfig import InstantaneousSource


class EddyDiffusion:

    def __init__(self, settings: IDMFConfig):
        self.settings = settings
        self.dim = self.settings.models.eddy_diffusion.dimensions
        self.volume = self.dim.x * self.dim.y * self.dim.z
        self.shape = (self.settings.time_samples,
                      self.settings.spatial_samples,
                      self.settings.spatial_samples,
                      self.settings.spatial_samples)
        self.conc = zeros(self.shape)
        self.zero = zeros(self.shape)
        self.one = ones(self.shape)
        self.diff_coeff = self.__diffusion_coefficient()

    def __call__(self, x: float, y: float,  z: float, t: float):
        try:
            return  getattr(self, f"_{self.settings.release_type}")(x, y, z, t)
        except AttributeError as e:
            f"Release type must be instantaneous, fixed_duration or infinite_duration"

    def _instantaneous(self, x: float, y: float, z: float, t: float):
        sources = self.settings.modes.instantaneous.sources
        for source in sources.values():
            t_shift = maximum(t - source.time, self.one)
            self.conc += self.heaviside(t, source.time) *\
                source.mass * self.__concentration(source, x, y, z, t_shift)
        return self.conc

    def _infinite_duration(self, x: float, y: float, z: float, t: float):
        sources = getattr(self.settings.modes, self.settings.release_type).sources
        for source in sources.values():
            t_shift = maximum(t - source.time, self.one)
            self.conc +=  self.heaviside(t, source.time) *\
                source.rate * self.__concentration(source, x, y, z, t_shift)
        return cumsum(self.conc, axis=0) *\
            (self.settings.total_time / self.settings.time_samples)
    
    def _fixed_duration(self, x: float, y: float, z: float, t: float):
        sources = getattr(self.settings.modes, self.settings.release_type).sources
        for source in sources.values():
            print(self.conc.shape)
            t_shift = maximum(t - source.start_time, self.one)
            self.conc += self.heaviside(t, source.start_time) *\
                source.rate * self.__concentration(source, x, y, z, t_shift) -\
                self.heaviside(t, source.end_time) *\
                source.rate * self.__concentration(source, x, y, z, t_shift)
        return cumsum(self.conc, axis=0) *\
            (self.settings.total_time / self.settings.time_samples)
    
    def heaviside(self, value: float, offset: float = 0):
        return where(value > offset, self.one, self.zero)

    def __concentration(self,
                       source: InstantaneousSource,
                       x: float,
                       y: float,
                       z: float,
                       t: float):
        r_x = self.__exp(x, t, self.dim.x, source.x)
        r_y = self.__exp(y, t, self.dim.y, source.y)
        r_z = self.__exp(z, t, self.dim.z, source.z)
        return self.__coeff(t) * r_x * r_y * r_z

    def __exp(self, position: float, t: float, bound: float, source_loc: float):

        image_num = self.settings.models.eddy_diffusion.images.quantity
        def image(arg):
            return exp((-power(arg, 2)) / 4 * self.diff_coeff * t)

        rv = []
        for image_index in range(-image_num, image_num + 1):
            rv.append(image(position + 2 * image_index * bound - source_loc) +
                      image(position + 2 * image_index * bound + source_loc))
        return sum(rv)

    def __coeff(self, t: float):
        fa_rate = self.settings.fresh_air_change_rate
        num = exp(-t * fa_rate / self.volume)
        den  = 8 * power(pi * self.diff_coeff * t, 3 / 2)
        return num / den

    def __diffusion_coefficient(self):
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
