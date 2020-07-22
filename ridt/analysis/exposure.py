from typing import Union

from scipy.integrate import cumtrapz
from numpy import ndarray

from ridt.config import RIDTConfig

from ridt.data import DataStore
from ridt.data import BatchDataStore


class Exposure:
    """The Exposure class

    The class which takes a :class:`~.DataStore` or :class:`~.BatchDataStore`
    and returns another instance of the same containing the computed 
    exposure.

    Attributes
    ----------
    setting : :class:`~.RIDTConfig`
        The settings for the run in question.
    
    data_store : Union[:class:`~.DataStore`, :class:`~.BatchDataStore`]
        The data store or batch data store of computed exposures.
    
    delta_t : :obj:`float`
        The time step for the current data set.

    """

    def __new__(cls, *args, **kwargs):
        instance = super(Exposure, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.data_store
    
    def __init__(self, setting: RIDTConfig, data_store: Union[DataStore, BatchDataStore]):
        """The Exposure class initialiser


        Parameters
        ----------
        setting : :class:`~.RIDTConfig`
            The settings for the run in question.
        
        data_store : Union[:class:`~.DataStore`, :class:`~.BatchDataStore`]
            The data store or batch data store to be analysed.
        
        """
        self.setting = setting
        self.delta_t = self.setting.total_time / self.setting.time_samples
        self.data_store = self.evaluate(data_store)
    
    @property
    def geometries(self):
        """:obj:`list` [:obj:`str`] : the list of geometries selected for
        evaluation in :attr:`setting`.

        """
        locations = self.setting.models.eddy_diffusion.monitor_locations
        return [g for g, e in locations.evaluate.items() if e]

    def compute(self, data: ndarray) -> ndarray:
        """Cumulative integral over the time axis.

        Parameters
        ----------
        data : :class:`~numpy.ndarray`
            The data array to integrate over.

        Returns
        -------
        :class:`~numpy.ndarray`
            The integrated array containing exposures.

        """
        return cumtrapz(data, dx=self.delta_t, axis=0, initial=0)

    def evaluate(self, data_store: Union[DataStore, BatchDataStore])\
            -> Union[DataStore, BatchDataStore]:
        """Iterates over all geometries and computes exposures.

        Parameters
        ----------
        data_store : Union[:class:`~.DataStore`, :class:`~.BatchDataStore`]
            The data store or batch data store to be analysed.

        Returns
        -------
        Union[:class:`~.DataStore`, :class:`~.BatchDataStore`]
            The computed exposures.

        Raises
        ------
        :obj:`TypeError`
            If the `data_store` is not a :class:`~.DataStore` or
            :class:`~.BatchDataStore`.

        """
        if isinstance(data_store, DataStore):
            rv = DataStore()
            for geometry in self.geometries:
                for name, data in getattr(data_store, geometry).items():
                    rv.add(geometry, name, self.compute(data))
            return rv
        elif isinstance(data_store, BatchDataStore):
            rv = BatchDataStore()
            for setting, store in data_store.items():
                rv.add_run(setting)
                rv[setting] = self.evaluate(data_store[setting])
            return rv
        else:
            raise TypeError(f"Expecting {DataStore} or {BatchDataStore}.")
    