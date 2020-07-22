from typing import List

from numpy import ndarray
from numpy import zeros
from numpy import array
from numpy import finfo
from numpy import float64

from ridt.config import RIDTConfig

import numpy as np


class WellMixed:
    """The core Well Mixed model class.

    This class provides all equation implementation of the Well Mixed Model.

    For details of the mathematics implemented here, please see the user guide.

    Attributes
    ----------
    settings : :class:`~.RIDTConfig`
        The settings for the run in question.
    
    dim : :class:`~.ridt.config.ridtconfig.Dimensions`
        The dimensions settings object that define the bounds of the system.

    volume : :obj:`float`
        The total volume of the system.

    fa_rate : :obj:`float`
        The fresh air change rate.

    shape : :obj:`Tuple`[:obj:`int`]
        The shape of the current grid.
    
    conc : :class:`~numpy.ndarray`
        The array where computed values are stored.
    
    """
    def __init__(self, settings: RIDTConfig):
        """The :class:`WellMixed` constructor.

        Parameters
        ----------
        settings : :class:`~.RIDTConfig`
            The settings for the run in question.
            
        """
        self.settings = settings
        self.dim = self.settings.dimensions
        self.volume = self.dim.x * self.dim.y * self.dim.z
        self.fa_rate = settings.fresh_air_flow_rate
        self.fa_rate = self.fa_rate if self.fa_rate else finfo(float64).tiny
        self.shape = (self.settings.time_samples,)
        self.conc = zeros(self.shape)

    def __call__(self, t: List[float]):
        """This call method is used to evaluate the model.

        t : :obj:`List`[:obj:`float`]
            The current time domain array.

        Returns
        -------
        :class:`~numpy.ndarray`
            The calculated concentration values.

        """

        modes = ["instantaneous", "infinite_duration", "fixed_duration"]

        for mode in modes:
            self.sources = getattr(self.settings.modes, mode).sources
            getattr(self, f"{mode}")(t)
        return array(self.conc)

    def concentration(self, t: float):
        """The exponential decay equation.

        Parameters
        ----------
        t : :obj:`float`
            The time.

        Returns
        -------
        :obj:`float`
            The computed value.

        """
        return np.exp(-(self.fa_rate / self.volume) * t)

    def instantaneous(self, t: np.ndarray):
        """Evaluate all instanteneous sources at time `t`.

        Parameters
        ----------
        t : :obj:`float`
            The time at which to evaluate the model.

        Returns
        -------
        None

        """
        for idx, time in enumerate(t):
            for source in self.sources.values():
                if time - source.time >= 0:
                    self.conc[idx] += (source.mass / self.volume) *\
                        self.concentration(time - source.time)

    def infinite_duration(self, t: ndarray):
        """Evaluate all infinite duration sources at time `t`.

        Parameters
        ----------
        t : :obj:`float`
            The time at which to evaluate the model.

        Returns
        -------
        None

        """
        for idx, time in enumerate(t):
            for source in self.sources.values():
                if time - source.time >= 0:
                    self.conc[idx] += (source.rate / self.fa_rate) *\
                        (1 - self.concentration(time - source.time))

    def fixed_duration(self, t: ndarray):
        """Evaluate all infinite duration sources at time `t`.

        Parameters
        ----------
        t : :obj:`float`
            The time at which to evaluate the model.

        Returns
        -------
        None

        """
        for source in self.sources.values():
            end_int = 0
            temp_conc = zeros(self.shape)
            for idx, time in enumerate(t):
                if time < source.start_time:
                    pass
                elif time <= source.end_time:
                    temp_conc[idx] += (source.rate / self.fa_rate) *\
                        (1 - self.concentration(time - source.start_time))
                else:
                    if not end_int:
                        end_int = idx - 1
                    temp_conc[idx] += temp_conc[end_int] * self.concentration(
                        time - source.end_time)
            self.conc = [sum(x) for x in zip(self.conc, temp_conc)]
