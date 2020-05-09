from numpy import linspace
from numpy import meshgrid

from config.idmfconfig import IDMFConfig
from config.idmfconfig import Point
from config.idmfconfig import Line 
from config.idmfconfig import Plane 


class Domain:

    def __init__(self, settings: IDMFConfig):
        self.set = settings
        self.dimensions = self.set.models.eddy_diffusion.dimensions
        self.space_samples = self.set.models.eddy_diffusion.spatial_samples
        self._x = linspace(0.0, self.dimensions.x, self.space_samples.x)
        self._y = linspace(0.0, self.dimensions.y, self.space_samples.y)
        self._z = linspace(0.0, self.dimensions.z, self.space_samples.z)
        self._time = linspace(0.0, self.set.total_time, self.set.time_samples)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y
    
    @property
    def z(self):
        return self._z
   
    @property
    def full(self):
        return meshgrid(self.x, self.y, self.z, indexing='ij')
    
    @property
    def time(self):
        return self._time
    
    def point(self, point: Point):
        return meshgrid(point.x, point.y, point.z)

    def line(self, line: Line):
        if line.parallel_axis == "x":
            return meshgrid(self.x, line.point.y, line.point.z)
        elif line.parallel_axis == "y":
            return meshgrid(line.point.x, self.y, line.point.z)
        else:
            return meshgrid(line.point.x, line.point.y, self.z)

    def plane(self, plane: Plane):
        if plane.axis == "xy":
            return meshgrid(self.x, self.y, plane.distance)
        elif plane.axis == "yz":
            return  meshgrid(plane.distance, self.y, self.z)
        else:
            return meshgrid(self.x, plane.distance, self.z)