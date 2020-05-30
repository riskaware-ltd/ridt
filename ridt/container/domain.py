from typing import Tuple

from numpy import linspace
from numpy import meshgrid

from ridt.config.ridtconfig import RIDTConfig
from ridt.config.ridtconfig import Point
from ridt.config.ridtconfig import Line 
from ridt.config.ridtconfig import Plane 


class Domain:

    def __init__(self, settings: RIDTConfig):
        self.set = settings
        self.dimensions = self.set.dimensions
        self.space_samples = self.set.spatial_samples
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
    
    def points(self, point: Point):
        return meshgrid(point.x, point.y, point.z)

    def lines(self, line: Line):
        if line.parallel_axis == "x":
            return meshgrid(self.x, line.point.y, line.point.z)
        elif line.parallel_axis == "y":
            return meshgrid(line.point.x, self.y, line.point.z)
        else:
            return meshgrid(line.point.x, line.point.y, self.z)

    def planes(self, plane: Plane):
        if plane.axis == "xy":
            return meshgrid(self.x, self.y, plane.distance)
        elif plane.axis == "yz":
            return  meshgrid(plane.distance, self.y, self.z)
        else:
            return meshgrid(self.x, plane.distance, self.z)
    
    def domain(self, *args, **kwargs):
        return self.full
    
    def values(self, geometry: str, id: str, index: Tuple[int]):
        if id == "well_mixed":
            return self.wellmixed_values(index)
        elif len(index) == 1:
            return self.point_values(id, index) 
        elif len(index) == 2:
            return self.line_values(id, index) 
        elif len(index) == 3:
            return self.plane_values(id, index) 
        elif len(index) == 4:
            return self.domain_values(id, index) 
        else:
            raise ValueError("Not a valid number of dimensions.")
        
    def wellmixed_values(self, index: Tuple[int]):
        return self.time[index[0]], "N/A", "N/A", "N/A" 

    def point_values(self, id: str, index: Tuple[int]):
        point = self.set.models.eddy_diffusion.monitor_locations.points[id]
        return self.time[index[0]], point.x, point.y, point.z
        
    def line_values(self, id: str, index: Tuple[int]):
        line = self.set.models.eddy_diffusion.monitor_locations.lines[id]
        if line.parallel_axis == "x":
            return self.time[index[0]], self.x[index[1]], line.point.y, line.point.z
        elif line.parallel_axis == "y":
            return self.time[index[0]], line.point.x, self.y[index[1]], line.point.z
        else:
            return self.time[index[0]], line.point.x, line.point.y, self.z[index[1]] 
        
    def plane_values(self, id: str, index: Tuple[int]):
        plane = self.set.models.eddy_diffusion.monitor_locations.planes[id]
        if plane.axis == "xy":
            return self.time[index[0]], self.x[index[1]], self.y[index[2]], plane.distance
        elif plane.axis == "yz":
            return self.time[index[0]], plane.distance, self.y[index[1]], self.z[index[2]]
        else:
            return self.time[index[0]], self.x[index[1]], plane.distance, self.z[index[2]] 
    
    def domain_values(self, id: str, index: Tuple[int]):
        return self.time[index[0]], self.x[index[1]], self.y[index[2]], self.z[index[3]] 