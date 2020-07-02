from typing import Union

from itertools import product

from tqdm import tqdm

from copy import deepcopy

from numpy import zeros
from numpy import array
from numpy import ndarray
from numpy.linalg import norm
from numpy import nan

from ridt.config import RIDTConfig
from ridt.config import InstantaneousSource
from ridt.config import InfiniteDurationSource
from ridt.config import FixedDurationSource 

from ridt.container import Domain

from ridt import bar_args

Source = Union[InstantaneousSource, InfiniteDurationSource, FixedDurationSource]


class UncertaintyMask:
    """Provides the ability to mask uncertain values in quantity grids.

    Attributes
    ----------
    settings : :class:`~.RIDTConfig`
        The settings for the run.

    sources : :obj:`List`[:class:`~numpy.ndarray`]
        The list of source term positions found in the settings instance.
    
    domain : :class:`~.Domain`
        The instance of :class:`~.Domain` corresponding to :attr:`settings`.

    """

    def __init__(self, setting: RIDTConfig):
        """The :class:`~.UncertaintyMask` constructor.

        Parameters
        ----------
        settings : :class:`~.RIDTConfig`
            The settings for the run.

        """
        self.setting = setting
        self.sources = self.get_source_locations()
        self.domain = Domain(setting)

    def get_source_locations(self):
        """Get the source settings objects from the run settings instance.

        Returns
        -------
        :obj:`List`[:class:`~numpy.ndarray`]
            The list of source term positions found in the settings instance.

        """
        rv = list()
        modes = ["instantaneous", "infinite_duration", "fixed_duration"]
        for mode in modes:
            sources = getattr(self.setting.modes, mode).sources
            rv += [array((s.x, s.y, s.z)) for s in sources.values()]
        return rv

    def mask(self, geometry: str, id: str, data: ndarray):
        """Masks all elements in the grid that are within 2m of a source.

        Parameters
        ----------
        geometry : :obj:`str`
            The type of grid to be masked.

        id : :obj:`str`
            The id of the grid to be masked.

        data : :class:`~ndarray.ndarray`
            The grid to be masked.

        Returns
        -------
        :class:`~numpy.ndarray`
            The masked array.

        """
        print(f"Excluding uncertain values in {id}...")
        return getattr(self, f"mask_{geometry}")(id, data)
    
    def mask_points(self, id: str, data: ndarray):
        """Mask values in point array close to a source.

        Parameters
        ----------
        id : :obj:`str`
            The id of the point.

        data : :class:`~.numpy.ndarray`
            The array to be masked.

        Returns
        -------
        :class:`~.numpy.ndarray`
            The masked copy.

        """
        point = self.setting.models.eddy_diffusion.monitor_locations.points[id]
        location = self.domain.point_cartesian(point)
        rv = deepcopy(data)
        for s in self.sources:
            if norm(s - location) <= 2.0:
                rv.fill(nan)
        return rv
        
    def mask_lines(self, id: str, data: ndarray):
        """Mask values in line array close to a source.

        Parameters
        ----------
        id : :obj:`str`
            The id of the line.

        data : :class:`~.numpy.ndarray`
            The array to be masked.

        Returns
        -------
        :class:`~.numpy.ndarray`
            The masked copy.

        """
        line = self.setting.models.eddy_diffusion.monitor_locations.lines[id]
        locations = self.domain.line_cartesian(line)
        rv = deepcopy(data)
        for idx, location in locations:
            for s in self.sources:
                if norm(s - array(location)) <= 2.0:
                    for idt, time in enumerate(self.domain.time):
                        rv[idt][idx] = nan
        return rv
        
    def mask_planes(self, id: str, data: ndarray):
        """Mask values in plane array close to a source.

        Parameters
        ----------
        id : :obj:`str`
            The id of the plane.

        data : :class:`~.numpy.ndarray`
            The array to be masked.

        Returns
        -------
        :class:`~.numpy.ndarray`
            The masked copy.

        """
        plane = self.setting.models.eddy_diffusion.monitor_locations.planes[id]
        locations = self.domain.plane_cartesian(plane)
        rv = deepcopy(data)
        for idx, location in locations:
            for s in self.sources:
                if norm(s - array(location)) <= 2.0:
                    for idt, time in enumerate(self.domain.time):
                        rv[idt][idx] = nan
        return rv
        
    def mask_domain(self, id: str, data: ndarray):
        """Mask values in domain array close to a source.

        Parameters
        ----------
        id : :obj:`str`
            The id of the domain.

        data : :class:`~.numpy.ndarray`
            The array to be masked.

        Returns
        -------
        :class:`~.numpy.ndarray`
            The masked copy.

        """
        locations = self.domain.domain_cartesian()
        rv = deepcopy(data)
        for idx, location in locations:
            for s in self.sources:
                if norm(s - array(location)) <= 2.0:
                    for idt, time in enumerate(self.domain.time):
                        rv[idt][idx] = nan
        return rv

