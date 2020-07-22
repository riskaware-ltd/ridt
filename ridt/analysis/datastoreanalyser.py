from copy import deepcopy

from numpy import nanstd
from numpy import nanmean

from ridt.config import RIDTConfig
from ridt.config import Units

from ridt.container import Domain

from ridt.data import DataStore
from ridt.data import UncertaintyMask

from .resultcontainers import Maximum
from .resultcontainers import Exceedance
from .resultcontainers import PercentExceedance
from .resultcontainers import MaxPercentExceedance


class DataStoreAnalyser:
    """The Data Store Analyser class.

    Iterates through all selected geometries and computes all quantities
    such as the maximum value etc.

    Attributes
    ----------
    setting : :class:`~.RIDTConfig`
        The settings for the run in question.
    
    domain : :class:`~.Domain`
        The instance of :class:`~.Domain` corresponding to :attr:`setting`.

    quantity: :obj:`str`
        The string id for the quantity stored in the data  store.

    data_store : :class:`~.DataStore`
        The data store to be analysed.
    
    thresholds : :obj:`list` [:obj:`float`]
        The threshold values corresponding to :attr:`quantity` defined in
        :attr:`setting`.
    
    units : :class:`~.Units`
        The instance of :class:`~.Units` corresponding to :attr:`setting`.
    
    maximum : :obj:`list` [:class:`~.Maximum`]
        The lists of :class:`~.Maximum` instances created.
    
    exceedance : :obj:`list` [:class:`~.Exceedance`]
        The lists of :class:`~.Exceedance` instances created.
    
    percent_exceedance: :obj:`list` [:class:`~.PercentExceedance`]
        The lists of :class:`~.PercentExceedance` instances created.
    
    max_percent_exceedance: :obj:`list` [:class:`~.MaxPercentExceedance`]
        The lists of :class:`~.MaxPercentExceedance` instances created.
    
    """
    def __init__(self,
                 setting: RIDTConfig,
                 data_store: DataStore,
                 quantity: str):
        """The :class`~.DataStoreAnalyser` class initialiser.
        
        Calls the :meth:`~.DataStoreAnalyser.evaluate` method.

        If flag is set in config file, will exclude values within 2m of all
        sources.

        Parameters
        ----------
        setting : :class:`~.RIDTConfig`
            The settings for the run in question.

        data_store : :class:`~.DataStore`
            The data store to be analysed.

        quantity : :obj:`str`
            The string id for the quantity stored in the data  store.

       """

        self.setting = setting
        self.units = Units(setting)
        self.domain = Domain(self.setting)
        self.quantity = quantity
        self.thresholds = self.threshold_converter()
        self.data_store = data_store

        if self.setting.models.eddy_diffusion.analysis.exclude_uncertain_values:
            self.exclude_uncertain_values()

        self.maximum = list()
        self.exceedance = list()
        self.percent_exceedance = list()
        self.max_percent_exceedance = list()

        self.evaluate()

    @property
    def geometries(self):
        """:obj:`list` [:obj:`str`] : the list of geometries selected for
        evaluation in :attr:`setting`.

        """
        locations = self.setting.models.eddy_diffusion.monitor_locations
        return [g for g, e in locations.evaluate.items() if e]

    def threshold_converter(self):
        """Converts the threshold into SI units.

        Converts the thresholds in :attr:`setting` corresponding to
        :attr:`quantity` into SI units.

        Returns
        -------
        :obj:`list` [:obj:`float`]
            The list of threshold values in SI units. 
        """
        tld = [t.value for t in getattr(self.setting.thresholds, self.quantity)]
        return getattr(self.units, f"{self.quantity}_converter")(tld)

    def evaluate(self):
        """Loops over all selected geometries and computes various quantities.

        The following quantities are evaluated:

        The maximum value.

        The fastest time to all threshold values.

        The fastest time to the defined percentage of domain to all threshold
        values.

        The largest percentage that exceeds all threshold values.

        A corresponding :class:`~.ResultContainer` derived class instances
        is created to hold each result.

        Returns
        -------
        None

        """
        p = self.setting.models.eddy_diffusion.analysis.percentage_exceedance
        for geometry in self.geometries:
            for id in getattr(self.data_store, geometry):
                index, value = self.data_store.maximum(geometry, id)
                cargs = (geometry, id, self.quantity)
                self.maximum.append(Maximum(self.setting, *cargs, index, value))
        for t in self.thresholds:
            for geometry in self.geometries:
                for id in getattr(self.data_store, geometry):
                    cargs = (geometry, id)
                    index = self.data_store.exceeds(*cargs, t)
                    self.exceedance.append(
                        Exceedance(self.setting, *cargs, self.quantity, index, t))
                    index = self.data_store.percentage_exceeds(*cargs, t, p)
                    self.percent_exceedance.append(
                        PercentExceedance(self.setting, *cargs, self.quantity, index, t, p))
                    index, value = self.data_store.percentage_exceeds_max(geometry, id, t)
                    self.max_percent_exceedance.append(
                        MaxPercentExceedance(self.setting, *cargs, self.quantity, value, index, t))
    
    def exclude_uncertain_values(self):
        """Sets values within 2m of source to nan.

        Iterates through all domains in data store and sets values within 
        2m of any source to nan.

        Returns
        -------
        None

        """
        new_data_store = deepcopy(self.data_store)
        um = UncertaintyMask(self.setting)
        for geometry in self.geometries:
            for id in getattr(new_data_store, geometry):
                data = um.mask(geometry, id, new_data_store.get(geometry, id))
                new_data_store.add(geometry, id, data)
        self.data_store = new_data_store

    @property
    def time_to_well_mixed(self):
        """Evaluates the time for system to become 'well mixed'

        Computes the time it takes for the full domain normalised standard
        deviation to become <= 0.1.

        Returns
        -------
        Union[:obj:`float`, :obj:`None`] 
            If there exists a time when well mixed state is acheived that time
            is returned, else :obj:`None`.

        """
        for i in range(self.setting.time_samples):
            d = self.data_store.get("domain", "domain")[i, :, :, :]
            value = nanstd(d) / nanmean(d)
            if value <= 0.1:
                return self.domain.time[i]
        return None
