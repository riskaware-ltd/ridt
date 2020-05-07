from numpy import zeros
from numpy import meshgrid
from numpy import linspace

from config.idmfconfig import IDMFConfig
from base.settings import ComputationalSpace

#################### Review imports before implementation
from equation import EddyDiffusion
from analysis import PointPlot
from analysis import LinePlot
from analysis import ContourPlot

from config.idmfconfig import Point
from config.idmfconfig import Line
from config.idmfconfig import Plane

import matplotlib.animation as animation
import matplotlib.pyplot as plt


class EddyDiffusionRun:

    def __init__(self, settings: IDMFConfig):

        self._settings = settings
        self.build_parameter_space()
        self.run(settings)
        # self.prepare()
    
    def build_parameter_space(self):
        self._time = linspace(0.0,
                              self.settings.total_time,
                              self.settings.time_samples)
        dim = self.settings.models.eddy_diffusion.dimensions
        sam = self.settings.models.eddy_diffusion.spatial_samples
        self._x = linspace(0.0, dim.x, sam.x)
        self._y = linspace(0.0, dim.y, sam.y)
        self._z = linspace(0.0, dim.z, sam.z)
        self._X, self._Y, self._Z = meshgrid(self._x,
                                             self._y,
                                             self._z,
                                             indexing='ij')
        self._space = (sam.x, sam.y, sam.z, self.settings.time_samples)

    def prepare(self):
        restrict = { 
            "modes": self.settings.release_type,
            "models": self.settings.dispersion_model
        }

        space = ComputationalSpace(self.settings, restrict)
        data = zeros(shape=(*space.shape, *self._space))
   
    @property
    def settings(self):
        return self._settings

    @property
    def time(self):
        return self._time

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    ############################## To be reviewed before implementation
    def run(self, settings: IDMFConfig):
        pp = PointPlot(settings)
        lp = LinePlot(settings)
        cp = ContourPlot(settings)

        monitor_points = settings.models.eddy_diffusion.monitor_locations
        ed = EddyDiffusion(settings)
        conc = ed(self._X, self._Y, self._Z, self._time)
        if settings.models.eddy_diffusion.point_plots.output:
            for point in monitor_points.points.values():
                point_conc = self.extract_point(conc, point)
                pp(point_conc, point)
                plt.show()
        if settings.models.eddy_diffusion.line_plots.output:
            for line in monitor_points.lines.values():
                fig = plt.figure()

                def animate(time):
                    return lp.plot(self.extract_line(conc, time, line), line)

                anim = animation.FuncAnimation(fig, animate, frames=self.settings.time_samples, repeat=True)
                plt.show()
        if settings.models.eddy_diffusion.contour_plots.output:
            for plane in monitor_points.planes.values():
                fig = plt.figure()

                def animate(time):
                    return cp.plot(self.extract_plane(conc, time, plane), plane)

                anim = animation.FuncAnimation(fig, animate, frames=self.settings.time_samples, repeat=True)
                plt.show()

    @staticmethod
    def extract_point(conc, point: Point):
        return conc[:, int(point.x), int(point.y), int(point.z)]

    @staticmethod
    def extract_line(conc, time, line: Line):
        sp = line.start_point
        if line.direction == "x":
            return conc[time, sp.x: sp.x + line.length, sp.y, sp.z]
        if line.direction == "y":
            return conc[time, sp.x, sp.y: sp.y + line.length, sp.z]
        if line.direction == "z":
            return conc[time, sp.x, sp.y, sp.z: sp.z + line.length]

    @staticmethod
    def extract_plane(conc, time, plane: Plane):
        time = int(time)
        if plane.axis == "xy":
            return conc[time, :, :, plane.distance]
        if plane.axis == "xz":
            return conc[time, :, plane.distance, :]
        if plane.axis == "yz":
            return conc[time, plane.distance, :, :]
        else:
            return f"plane.axis must be either, xy, xz or zy"
