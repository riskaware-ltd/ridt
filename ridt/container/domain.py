from typing import Tuple
from typing import Iterable 

from itertools import product

from numpy import linspace
from numpy import meshgrid
from numpy import ndarray
from numpy import unravel_index

from ridt.config.ridtconfig import RIDTConfig
from ridt.config.ridtconfig import Point
from ridt.config.ridtconfig import Line 
from ridt.config.ridtconfig import Plane 


class Domain:
    """A class the povides various spatial and temporal domain infomation.

    This class provides various functions that give domain infomation relating
    to monitor locations and the total domain. The meshgrids over which the
    equaations are evaluated are generated from the settings object by this
    class.
    
    Attributes
    ----------
    set : :obj:`~.RIDTConfig`
        The settings object for the current run.
    
    """

    def __init__(self, settings: RIDTConfig):
        """[summary]

        Parameters
        ----------
        setting : :class:`~.RIDTConfig`
            The settings object containing the units selections and definitions.

        """
        self.set = settings
        self._x = linspace(0.0, self.set.dimensions.x, self.set.spatial_samples.x)
        self._y = linspace(0.0, self.set.dimensions.y, self.set.spatial_samples.y)
        self._z = linspace(0.0, self.set.dimensions.z, self.set.spatial_samples.z)
        self._time = linspace(0.0, self.set.total_time, self.set.time_samples)

    @property
    def x(self):
        """:obj:`Iterable`[:obj:`float`] : The discretised x domain."""
        return self._x

    @property
    def y(self):
        """:obj:`Iterable`[:obj:`float`] : The discretised y domain."""
        return self._y
    
    @property
    def z(self):
        """:obj:`Iterable`[:obj:`float`] : The discretised z domain."""
        return self._z
   
    @property
    def full(self):
        """:obj:`Tuple`[:class:`~numpy.ndarray`] : The full meshgrid domain."""
        return meshgrid(self.x, self.y, self.z, indexing='ij')
    
    @property
    def time(self):
        """:obj:`Iterable`[:obj:`float`] : The discretised time domain."""
        return self._time
    
    def point_cartesian(self, point: Point):
        """Returns the values for the point's position as a tuple

        Parameters
        ----------
        point : :class:`~.Point`
            The point being queried.

        Returns
        -------
        :obj:`tuple`[:obj:`float`]
            The (x, y, z) position of the point.
            
        """
        return (point.x, point.y, point.z)
    
    def line_cartesian(self, line: Line):
        """Returns a list of tuples with all poistions on the line and
        their corresponding indices.

        Parameters
        ----------
        line : :class:`~.Line`
            The line being queried.

        Returns
        -------
        :obj:`list`[:obj:`tuple`[:obj:`tuple`[:obj:`int`], :obj:`tuple`[:obj:`float`]]]
            The grid indices and values of all points in the line.

        """
        if line.parallel_axis == "x":
            return [
                (unravel_index(i, self.x.shape), item) for i, item in 
                enumerate(product(self.x, [line.point.y], [line.point.z]))
            ]
        elif line.parallel_axis == "y":
            return [
                (unravel_index(i, self.y.shape), item) for i, item in 
                enumerate(product([line.point.x], self.y, [line.point.z]))
            ]
        else:
            return [
                (unravel_index(i, self.z.shape), item) for i, item in 
                enumerate(product([line.point.x], [line.point.y], self.z))
            ]
    
    def plane_cartesian(self, plane: Plane):
        """Returns a list of tuples with all poistions on the plane and
        their corresponding indices.

        Parameters
        ----------
        plane : :class:`~.Plane`
            The plane being queried.

        Returns
        -------
        :obj:`list`[:obj:`tuple`[:obj:`tuple`[:obj:`int`], :obj:`tuple`[:obj:`float`]]]
            The grid indices and values of all points in the plane.

        """
        if plane.axis == "xy":
            return [
                (unravel_index(i, (len(self.x), len(self.y))), item) for i, item in 
                enumerate(product(self.x, self.y, [plane.distance]))
            ]
        elif plane.axis == "yz":
            return [
                (unravel_index(i, (len(self.y), len(self.z))), item) for i, item in 
                enumerate(product([plane.distance], self.y, self.z))
            ]
        else:
            return [
                (unravel_index(i, (len(self.x), len(self.z))), item) for i, item in 
                enumerate(product(self.x, [plane.distance], self.z))
            ]
    
    def domain_cartesian(self, *args, **kwargs):
        """Returns a list of tuples with all poistions on the domain and
        their corresponding indices.

        Returns
        -------
        :obj:`list`[:obj:`tuple`[:obj:`tuple`[:obj:`int`], :obj:`tuple`[:obj:`float`]]]
            The grid indices and values of all points in the domain.

        """
        return [
            (unravel_index(i, (len(self.x), len(self.y), len(self.z))), item)
            for i, item in enumerate(product(self.x, self.y, self.z))
        ]
    
    def points(self, point: Point):
        """Returns the meshgrid corresponding to a point-like monitor locaiton.

        Parameters
        ----------
        point : :class:`~.Point`
            The point-line monitor location settings object.

        Returns
        -------
        :obj:`Tuple`[:class:`~numpy.ndarray`]
            The 3D meshgrid for the point.
        
        """
        return meshgrid(point.x, point.y, point.z, indexing="ij")

    def lines(self, line: Line):
        """Returns the meshgrid corresponding to a line-like monitor locaiton.

        Parameters
        ----------
        line : :class:`~.Line`
            The line-line monitor location settings object.

        Returns
        -------
        :obj:`Tuple`[:class:`~numpy.ndarray`]
            The 3D meshgrid for the line.
        
        """
        if line.parallel_axis == "x":
            return meshgrid(self.x, line.point.y, line.point.z, indexing="ij")
        elif line.parallel_axis == "y":
            return meshgrid(line.point.x, self.y, line.point.z, indexing="ij")
        else:
            return meshgrid(line.point.x, line.point.y, self.z, indexing="ij")

    def planes(self, plane: Plane):
        """Returns the meshgrid corresponding to a plane-like monitor locaiton.

        Parameters
        ----------
        plane : :class:`~.Plane`
            The plane-plane monitor location settings object.

        Returns
        -------
        :obj:`Tuple`[:class:`~numpy.ndarray`]
            The 3D meshgrid for the plane.
        
        """
        if plane.axis == "xy":
            rv = meshgrid(self.x, self.y, plane.distance, indexing="ij")
            return rv
        elif plane.axis == "yz":
            return  meshgrid(plane.distance, self.y, self.z, indexing="ij")
        else:
            return meshgrid(self.x, plane.distance, self.z, indexing="ij")
    
    def domain(self, *args, **kwargs):
        """An interface for the :attr:`full` parameter.
        
        Returns
        -------
        :obj:`Tuple`[:class:`~numpy.ndarray`]
            The 3D meshgrid for the whole domain.
        
        """
        return self.full
    
    def values(self, geometry: str, id: str, index: Tuple[int]):
        """Returns the spatio-temporal values for an index and monitor location

        This method takes a monitor location and some temporal meshgrid indices 
        and returns the corresponding spatial values.

        Parameters
        ----------
        geometry : :obj:`str`
            The class of monitor location.

        id : :obj:`str`
            The monitor location id string.

        index : :obj:`Tuple`[:obj:`int`]
            The temporal meshgrid index being queried.

        Returns
        -------
        :obj:`Tuple`[:obj:`float`]
            The time, x position, y position, and z position.

        Raises
        ------
        :obj:`ValueError`
            If an index with an invalid number of dimensions is passed.

        """
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
        """Returns the spatio-temporal values for an index, for well mixed model

        Parameters
        ----------
        index : :obj:`Tuple`[:obj:`int`]
            The index being queried.

        Returns
        -------
        :obj:`Tuple`[:obj:`float`]
            The time, x position, y position, and z position.

        """
        return self.time[index[0]], "N/A", "N/A", "N/A" 

    def point_values(self, id: str, index: Tuple[int]):
        """Returns the spatio-temporal values for an index, for points. 

        Parameters
        ----------
        index : :obj:`Tuple`[:obj:`int`]
            The index being queried.

        id : :obj:`str`
            The point id string.

        Returns
        -------
        :obj:`Tuple`[:obj:`float`]
            The time, x position, y position, and z position.

        """
        point = self.set.models.eddy_diffusion.monitor_locations.points[id]
        return self.time[index[0]], point.x, point.y, point.z
        
    def line_values(self, id: str, index: Tuple[int]):
        """Returns the spatio-temporal values for an index, for lines. 

        Parameters
        ----------
        index : :obj:`Tuple`[:obj:`int`]
            The index being queried.

        id : :obj:`str`
            The line id string.

        Returns
        -------
        :obj:`Tuple`[:obj:`float`]
            The time, x position, y position, and z position.

        """
        line = self.set.models.eddy_diffusion.monitor_locations.lines[id]
        if line.parallel_axis == "x":
            return self.time[index[0]], self.x[index[1]], line.point.y, line.point.z
        elif line.parallel_axis == "y":
            return self.time[index[0]], line.point.x, self.y[index[1]], line.point.z
        else:
            return self.time[index[0]], line.point.x, line.point.y, self.z[index[1]] 
        
    def plane_values(self, id: str, index: Tuple[int]):
        """Returns the spatio-temporal values for an index, for planes. 

        Parameters
        ----------
        index : :obj:`Tuple`[:obj:`int`]
            The index being queried.

        id : :obj:`str`
            The plane id string.

        Returns
        -------
        :obj:`Tuple`[:obj:`float`]
            The time, x position, y position, and z position.

        """
        plane = self.set.models.eddy_diffusion.monitor_locations.planes[id]
        if plane.axis == "xy":
            return self.time[index[0]], self.x[index[1]], self.y[index[2]], plane.distance
        elif plane.axis == "yz":
            return self.time[index[0]], plane.distance, self.y[index[1]], self.z[index[2]]
        else:
            return self.time[index[0]], self.x[index[1]], plane.distance, self.z[index[2]] 
    
    def domain_values(self, id: str, index: Tuple[int]):
        """Returns the spatio-temporal values for an index, for the domain. 

        Parameters
        ----------
        index : :obj:`Tuple`[:obj:`int`]
            The index being queried.

        id : :obj:`str`
            The domain id string.

        Returns
        -------
        :obj:`Tuple`[:obj:`float`]
            The time, x position, y position, and z position.

        """
        return self.time[index[0]], self.x[index[1]], self.y[index[2]], self.z[index[3]] 