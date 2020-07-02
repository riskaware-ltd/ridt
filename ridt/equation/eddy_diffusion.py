import warnings

import numpy

from typing import List
from typing import Tuple 
from typing import Union
from copy import copy

from itertools import product

from tqdm import tqdm

from numpy import ndarray
from numpy import array
from numpy import zeros
from numpy import exp
from numpy import log
from numpy import power
from numpy import pi
from numpy import square
from numpy import nanmean
from numpy import float64
from numpy import finfo

from scipy.integrate import cumtrapz
from scipy.integrate import romberg

from ridt.config import ConfigFileParser
from ridt.config import RIDTConfig
from ridt.config import InstantaneousSource
from ridt.config import InfiniteDurationSource
from ridt.config import FixedDurationSource 

from ridt.container import Domain

from ridt import bar_args

numpy.seterr(divide='ignore')
numpy.seterr(invalid='ignore')


Source = Union[InstantaneousSource, InfiniteDurationSource, FixedDurationSource]
Value = Union[ndarray, float]

MAX_IMAGE = 20

class EddyDiffusion:
    """The core Eddy Diffusion model class.

    This class provides all equation implementation of the Eddy Diffusion Model.

    For details of the mathematics implemented here, please see the user guide.

    Attributes
    ----------
    settings : :class:`~.RIDTConfig`
        The settings for the run in question.
    
    dim : :class:`~.Dimensions`
        The dimensions settings object that define the bounds of the system.
    
    disc : :class:`~.SpatialSamples`
        The spatial samples settings object that define how each axis is
        discretised.

    volume : :obj:`float`
        The total volume of the system.
    
    shape : :obj:`Tuple`[:obj:`int`]
        The shape of the current grid.
    
    cumtrapz_kwargs : :obj:`dict`
        A dictionary of keyword args for the cumulative trapezoidal integration
        function. 
    
    diff_coeff : :obj:`float`
        The diffusion coefficient.
    
    modes : :obj:`List`[:obj:`str`]
        The different string ids for the source modes.
    
    x : :class:`~numpy.ndarray`
        The current x-axis meshgrid.

    y : :class:`~numpy.ndarray`
        The current y-axis meshgrid.

    
    z : :class:`~numpy.ndarray`
        The current z-axis meshgrid.
    
    t : :obj:`List`[:obj:`float`]
        The current time domain array.

    rv : :class:`~numpy.ndarray`
        The calculated concentration values.

    """

    def __init__(self, settings: RIDTConfig):
        """The :class:`EddyDiffusion` constructor.

        Parameters
        ----------
        settings : :class:`~.RIDTConfig`
            The settings for the run in question.
            
        """
        self.settings = settings
        self.dim = self.settings.dimensions
        self.disc = self.settings.spatial_samples
        self.volume = self.dim.x * self.dim.y * self.dim.z
        self.cumtrapz_kwargs = {
            "axis": 0,
            "initial": 0,
            "dx": self.settings.total_time / self.settings.time_samples
        }
        self.diff_coeff = self.diffusion_coefficient()
        self.modes = ["instantaneous", "infinite_duration", "fixed_duration"]

    def __call__(self, x: ndarray, y: ndarray,  z: ndarray, t: List[float]):
        """This call method is used to evaluate the model.

        Parameters
        ----------
        x : :class:`~numpy.ndarray`
            The current x-axis meshgrid.

        y : :class:`~numpy.ndarray`
            The current y-axis meshgrid.

        
        z : :class:`~numpy.ndarray`
            The current z-axis meshgrid.
        
        t : :obj:`List`[:obj:`float`]
            The current time domain array.

        Returns
        -------
        :class:`~numpy.ndarray`
            The calculated concentration values.

        """
        self.get_grid_shape(x)
        self.assign_grids(x, y, z, t)

        self.rv = array(self.zero_arrays())

        for mode in self.modes:
            self.sources = getattr(self.settings.modes, mode).sources
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                getattr(self, f"{mode}")()

        return self.rv
    
    def assign_grids(self, x: ndarray, y: ndarray,  z: ndarray, t: List[float]) -> None:
        """Assign the meshgrids to the relevant attributes.

        Parameters
        ----------
        x : :class:`~numpy.ndarray`
            The current x-axis meshgrid.

        y : :class:`~numpy.ndarray`
            The current y-axis meshgrid.

        
        z : :class:`~numpy.ndarray`
            The current z-axis meshgrid.
        
        t : :obj:`List`[:obj:`float`]
            The current time domain array.
        
        Returns
        -------
        None

        """
        self.x = x
        self.y = y
        self.z = z
        self.t = t
    
    def get_grid_shape(self, grid: ndarray) -> Tuple[int]:
        """Returns the shape of the passed grid.

        Parameters
        ----------
        grid : :class:`~numpy.ndarray`
            The grid to be assessed.
        
        Returns
        -------
        :class:`Tuple`[:obj:`int`]
            The shape of the grid.

        """
        self.shape = grid.shape
    
    def get_catesian_index_space(self):
        """Generate a cartesian product set of all grid indices.

        Returns
        -------
        :class:`Iterable`[:class:`Tuple`[:obj:`int`]]
            An iterable of tuples of indices.

        """

        return product(*[range(d) for d in self.shape])

    def get_raw_values(self, idx: int, idy: int, idz: int) -> Tuple[float]:
        """For a given set of grid indices, return raw values from the meshes.

        Parameters
        ----------
        idx : :obj:`int`
            The x index.

        idy : :obj:`int`
            The y index.

        idz : :obj:`int`
            The z index.

        Returns
        -------
        :class:`Tuple`[:obj:`float`]
            The x, y, and z values corresponding to the provided indices.
            
        """
        index = (idx, idy, idz)
        return self.x[index], self.y[index], self.z[index]

    @property
    def time(self):
        """Returns a :mod:`tqdm` iterable over the :attr:`time` iterable.

        Returns
        -------
        :obj:`Iterable`[:class:`Tuple`[:obj:`int`, :obj:`float`]
            The :mod:`tqdm` iterable over the :attr:`time` iterable
            
        """
        return tqdm(enumerate(self.t), total=len(self.t), **bar_args)

    def romberg(self, time: float, source: Source, idx: int, idy: int, idz: int) -> float:
        """ Performs romberg integration at the given grid location.

        This is performed between zero and the provided time.

        Parameters
        ----------
        time : :obj:`float`
            The time to integrate to.

        source : :class:`~.Source`    
            The source term in question.

        idx : :obj:`int`
            The x index.

        idy : :obj:`int`
            The y index.

        idz : :obj:`int`
            The z index.

        Returns
        -------
        :obj:`float`
            The computed concentration.

        """
        x, y, z = self.get_raw_values(idx, idy, idz)
        integrand = lambda tin: self.conc(source, x, y, z, tin)
        return romberg(integrand, 1e-100, time, tol=1e-100)
    
    def pointwise(self, source: Source, time: float) -> ndarray:
        """Evaluates the equation pointwise at every location in the meshgrids.

        Parameters
        ----------
        time : :obj:`float`
            The time to integrate to.

        source : :class:`~.Source`    
            The source term in question.

        Returns
        -------
        :class:`~numpy.ndarray`
            The array containing the computed concentrations.
        """
        return self.conc(source, self.x, self.y, self.z, time)

    def evaluate(self, rtime: float, idt: int, conc: List[ndarray], source: Source):
        """Calls the relevant method for evaluating the equations.
    
        Different methods are called depending on the integration method
        selected. 

        Parameters
        ----------
        rtime : :obj:`float`
            The time relative to the source release/start time.

        idt : :obj:`int`
            The absolute time index.

        conc : :class:`List`[:class:`~numpy.ndarray`]
            The list of grids to store the computed values in.

        source : :class:`~.Source`
            The source being evaluated.
            
        Returns
        -------
        None

        """

        if self.settings.integration_method == "romberg":
            for item in self.get_catesian_index_space():
                conc[idt][item] += source.rate * self.romberg(rtime, source, *item)
        else:
            conc[idt] += source.rate * self.pointwise(source, rtime)
    
    def process(self, conc: List[ndarray]) -> ndarray:
        """Perform the integration method dependent post processing. 

        Parameters
        ----------
        conc : :class:`List`[:class:`~numpy.ndarray`]
            The list of grids to store the computed values in.

        Returns
        -------
        :class:`~numpy.ndarray`
            The final grids to be added to the total.

        """
        if self.settings.integration_method == "romberg":
            return array(conc)
        else:
            return cumtrapz(array(conc), **self.cumtrapz_kwargs)
    
    def log_start(self, name: str, id: str) -> None:
        """Print a log message the evaluation of a grid has started.

        Parameters
        ----------
        name : :obj:`str`
            The type of source.

        id : :obj:`str`
            The source id string.
        
        Returns
        -------
        None

        """
        print(f"Evaluating {name} source (id: {id}) for each time...") 

    def instantaneous(self): 
        """Evaluate all instanteneous sources.

        Returns
        -------
        None

        """
        for id, source in self.sources.items():
            conc = self.zero_arrays()
            self.log_start("instanteneous", id)
            for idt, time in self.time:
                stime = time - source.time
                if stime > 0:
                    conc[idt] += source.mass * self.pointwise(source, stime)
            self.rv += array(conc)
 
    def infinite_duration(self):
        """Evaluate all infinite duration sources.

        Returns
        -------
        None

        """
        for id, source in self.sources.items():
            conc = self.zero_arrays()
            self.log_start("infinite duration", id)
            for idt, time in self.time:
                stime = time - source.time
                if stime > 0:
                    self.evaluate(stime, idt, conc, source)
            self.rv += self.process(conc)
    
    def fixed_duration(self):
        """Evaluate all fixed duration sources.

        Returns
        -------
        None

        """
        for id, source in self.sources.items():
            conc = self.zero_arrays()
            conc_decay = self.zero_arrays()
            self.log_start("fixed duration", id)
            for idt, time in self.time:
                stime = time - source.start_time
                etime = time - source.start_time - source.end_time
                if stime > 0:
                    self.evaluate(stime, idt, conc, source)
                if etime > 0:
                    self.evaluate(etime, idt, conc_decay, source)
            self.rv += self.process(conc) - self.process(conc_decay)
    
    def conc(self, source: Source, x: Value, y: Value, z: Value, t: float) -> Value:
        """Evaluate various the model at a given location, time and source.

        Parameters
        ----------
        source : :class:`~.Source`
            The source being evaluated.

        x : :class:`~.Value`
            The x value.

        y : :class:`~.Value`
            The y value.

        z : :class:`~.Value`
            The z value.

        t : :obj:`float`
            the time value

        Returns
        -------
        :class:`~.Value`
            The calculated concentration.
        """
        r_x = self.exp(x, t, self.dim.x, source.x)
        r_y = self.exp(y, t, self.dim.y, source.y)
        r_z = self.exp(z, t, self.dim.z, source.z)
        return self.coefficient(t) * r_x * r_y * r_z

    def exp(self, pos: Value, time: float, bound: float, spos: float) -> Value:
        """The sum of exponentials in the Eddy diffusion model.

        Parameters
        ----------
        pos : :class:`~.Value`
            The position.

        t : :obj:`float`
            The time.

        bound : :obj:`float`
            The upper spatial bound.

        spos : :obj:`float`
            The source position.

        Returns
        -------
        :class:`~.Value`
            The calculated value.
        
        """

        image_setting = self.settings.models.eddy_diffusion.images

        term = lambda x: exp(-power(x, 2) / (4 * self.diff_coeff * time))
        exp_arg = lambda x: pos + 2 * x * bound
        image = lambda x: term(exp_arg(x) - spos) + term(exp_arg(x) + spos)

        image_index = 0

        rv = 0.0 if type(pos) is float else zeros(pos.shape)

        rv += image(image_index)

        if image_setting.mode == "manual":
            if image_setting.quantity:
                image_index = image_setting.quantity
                for idx in range(1, image_index + 1):
                    rv += image(idx) + image(-idx)
        else:
            while image_index < MAX_IMAGE:
                image_index += 1
                new_term = 0.0 if type(pos) is float else zeros(pos.shape)
                new_term += image(image_index) + image(-image_index)
                if self.geometric_variance(rv, rv + new_term) < 1 + 1e-10:
                    rv += new_term
                    break
                rv += new_term
        return rv
    
    def geometric_variance(self, old: Value, new: Value) -> float:
        """Calculate the geometric variance between two grids (or numbers)

        Parameters
        ----------
        old : :class:`~.Value`
            The old values.

        new : :class:`~.Value`
            The new values.

        Returns
        -------
        :obj:`float` 
            The geometric variance.

        """
        return exp(nanmean(square(log(old)-log(new))))

    def coefficient(self, t: float) -> float:
        """Computes the temporal decay coefficient.

        Parameters
        ----------
        t : :obj:`float` 
            The current time.

        Returns
        -------
        :obj:`float`
            The coefficient.

        """
        fa_rate = self.settings.fresh_air_change_rate
        num = exp(-t * fa_rate / self.volume)
        den  = 8 * power(pi * self.diff_coeff * t, 3.0 / 2.0)
        return num / den

    def diffusion_coefficient(self):
        """Computes the diffusion coefficient.

        Returns
        -------
        :obj:`float`
            The selected diffusion coefficient.

        """
        tkeb_settings = self.settings.models.eddy_diffusion.coefficient.tkeb
        vent_number = tkeb_settings.number_of_supply_vents
        air_change_rate = tkeb_settings.total_air_change_rate
        coeff = self.settings.models.eddy_diffusion.coefficient
        bound = tkeb_settings.bound

        if coeff.calculation == "EXPLICIT":
            return coeff.value
        else:
            tkeb_term = air_change_rate /\
                power(self.volume * power(vent_number, 2), 1.0 / 3.0)
            if bound == "lower":
                return 0.827 * tkeb_term + 0.0565
            elif bound == "regression":
                return 0.824 * tkeb_term
            elif bound == "upper": 
                return max(0.822 * tkeb_term - 0.0565, 0.001)

    def zero_arrays(self):
        """Creates new time series lists of grids filed with zeros.

        Returns
        -------
        :class:`List`[:class:`~numpy.ndarray`]
            The list of grids to store the computed values in.

        """
        return [zeros(self.shape) for i in range(self.settings.time_samples)]
