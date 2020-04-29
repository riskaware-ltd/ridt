from config.ConfigFileParser import ConfigFileParser
from config.idmfconfig import IDMFConfig

import numpy as np


class EddyDiffusion:

    def __init__(self):
        pass

    def __call__(self, settings: IDMFConfig):

        coefficient = self.__coeff(settings)
        xx, yy, zz, tt = self.__form_mesh_grid(settings)

        try:
            return getattr(self, f"_{settings.release_type}")(settings, xx, yy, zz, tt, coefficient)
        except AttributeError as e:
            f"Release type must be instantaneous, fixed_duration or infinite_duration"

    def _instantaneous(self, settings: IDMFConfig, xx, yy, zz, tt, coefficient):

        sources = settings.modes.instantaneous.sources

        dimension = [
            settings.models.eddy_diffusion.dimensions.x,
            settings.models.eddy_diffusion.dimensions.y,
            settings.models.eddy_diffusion.dimensions.z
        ]

        concentration = []
        for source_name, source in sources.items():
            concentration.append([])
            r_x = self.__exp(settings, xx, tt, dimension[0], source.x,
                             source.time, coefficient[0])
            r_y = self.__exp(settings, yy, tt, dimension[1], source.y,
                             source.time, coefficient[0])
            r_z = self.__exp(settings, zz, tt, dimension[2], source.z,
                             source.time, coefficient[0])
            concentration[-1].append(
                self.__instantaneous_concentration(settings, source.mass, coefficient[0],
                                                   tt, r_x, r_y, r_z)
            )
        concentration = np.squeeze(concentration)
        # concentration = self.__pointwise_addition(concentration[0], concentration[1])
        print(concentration[0])
        return concentration

    def __instantaneous_concentration(
            self, settings: IDMFConfig, mass: float, coefficient: float,
            time: float, r_x: float, r_y: float, r_z: float):

        fa_rate = settings.fresh_air_change_rate
        return (
            (mass * np.exp(-fa_rate * time) / 8 * np.power((np.pi * coefficient * time), 3/2)) *
            r_x * r_y * r_z
        )

    def __infinite(self, x, y, z, t, n):
        return float
    
    def __fixed(self, x, y, z, t, n):
        return float

    def __image(self, axis, x, y, z, t, n):
        # Compute the image term on a given axis.
        return float
    
    def __concentration(self, x, y, z, t):
        # uses __coeff and __image  and settings to compute the concentration
        # at  a given time and place.
        return float

    def __exp(self,
              settings: IDMFConfig,
              pos: float,
              t: float,
              dimension: float,
              source_pos: float,
              source_time: float,
              coefficient: float):

        image_num = settings.models.eddy_diffusion.images.quantity

        rv = []
        for n in range(-image_num, image_num + 1):
            rv.append(
                np.exp((-np.power(pos + 2 * n * dimension - source_pos, 2)) /
                       4 * coefficient * t) +
                np.exp((-np.power(pos + 2 * n * dimension + source_pos, 2)) /
                       4 * coefficient * t)
            )
        return sum(rv)

    def __coeff(self, settings: IDMFConfig):
        coeff = settings.models.eddy_diffusion.coefficient
        if coeff.calculation == "EXPLICIT":
            return coeff.value
        if coeff.calculation == "TKEB":
            return self.__tkeb(settings)

    def __tkeb(self, settings: IDMFConfig):
        eddy_diffusion = settings.models.eddy_diffusion
        vent_number = eddy_diffusion.coefficient.tkeb.number_of_supply_vents

        volume = [
                eddy_diffusion.dimensions.x *
                eddy_diffusion.dimensions.y *
                eddy_diffusion.dimensions.z
        ]

        tkeb_term = (settings.total_air_change_rate /
                     np.power(volume * np.power(vent_number, 2), 1/3))

        upper_pi = 0.827 * tkeb_term + 0.0565
        regression = 0.824 * tkeb_term
        lower_pi = 0.822 * tkeb_term - 0.0565

        if lower_pi < 0.001:
            lower_pi = 0.001

        return upper_pi, regression, lower_pi

    def __form_mesh_grid(self, settings: IDMFConfig):
        x = settings.models.eddy_diffusion.dimensions.x
        y = settings.models.eddy_diffusion.dimensions.y
        z = settings.models.eddy_diffusion.dimensions.z
        t = settings.total_time

        x_range = np.linspace(
            0, x, settings.spatial_samples)
        y_range = np.linspace(
            0, y, settings.spatial_samples)
        z_range = np.linspace(
            0, z, settings.spatial_samples)
        t_range = np.linspace(
            0, t, settings.time_samples)

        tt, xx, yy, zz = np.meshgrid(t_range, x_range, y_range, z_range, indexing="ij")

        return xx, yy, zz, tt

    @staticmethod
    def __pointwise_addition(a, b):
        return a + b


c = ConfigFileParser()
config = c("../default/config.json")

w = EddyDiffusion()
g = w(config)

import matplotlib.pyplot as plt
import matplotlib.animation as animation


"""fig1 = plt.figure()
for i in range(100):
    for j in range(5):
        contour, = plt.contourf([], [], g[i][j])
        plt.title(f"Time: {i}, Z: {j}")
        contour_anim = anim.FuncAnimation(fig1, update_contour, 10)
        plt.show()"""


x = np.linspace(0, 5, 5)
y = np.linspace(0, 5, 5)
xx, yy = np.meshgrid(x, y)

fig = plt.figure()
ax = plt.axes(xlim=(0, 5), ylim=(0, 5), xlabel='x', ylabel='y')

cvals = np.linspace(0, 1, 6)      # set contour values
cont = plt.contourf(x, y, g[0][0], cvals)    # first image on screen
plt.colorbar()


def get_g(i):
    return g[i][2]


def animate(i):
    global cont
    z = get_g(i)
    for c in cont.collections:
        c.remove()  # removes only the contours, leaves the rest intact
    cont = plt.contourf(xx, yy, z, cvals)
    # plt.title('t = %i:  %.2f' % (i,z[5,5]))
    return cont


anim = animation.FuncAnimation(fig, animate, frames=100, repeat=True)
plt.show()
# anim.save("", writer=animation.FFMpegWriter())
