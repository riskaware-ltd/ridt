from os.path import join

from typing import Union

from tqdm import tqdm

from numpy import zeros
from numpy import meshgrid
from numpy import squeeze 

from ridt.base import ComputationalSpace

from ridt.config import RIDTConfig

from ridt.equation import EddyDiffusion

from ridt.data import BatchDataStore
from ridt.data import BatchDataStoreWriter
from ridt.data import BatchDataStorePlotter

from ridt.container import Domain

from ridt.analysis import BatchDataStoreAnalyser
from ridt.analysis import Exposure


class EddyDiffusionRun:
    """The class which orchestrates an Eddy Diffusion model run.

    Attributes
    ----------
    setting : :class:`~.RIDTConfig`
        The settings for the run in question.

    data_store : :class:`~.BatchDataStore`
        The batch run data store for concentration values.

    outdir: :obj:`str`
        The path to the output directory for the run.
    
    space : :class:`~.ComputationalSpace`
        The :class:`~.ComputationalSpace` instance corresponding to the
        :attr:`settings` attribute.
    
    exposure_store : :obj:`Union`[:class:`~.BatchDataStore`, None]
        The batch run data store for exposure values.
    
    """


    def __init__(self, settings: RIDTConfig, outdir: str):
        """The constructor for the :class:`EddyDiffusionRun` class.

        Parameters
        ----------
        settings : :class:`~.RIDTConfig`
            The settings for the run in question.

        outdir : :obj:`str`
            The path to the output directory for the run.

        """
        self.settings = settings
        self.outdir = outdir
        self.data_store = BatchDataStore()
        self.exposure_store = None
        self.space = self.prepare()
        self.evaluate()
        self.compute_exposure()
        self.write()
        self.plot()
        self.analyse()

    @property
    def geometries(self):
        """:obj:`list` [:obj:`str`] : the list of geometries selected for
        evaluation in :attr:`settings`.

        """
        locations = self.settings.models.eddy_diffusion.monitor_locations
        return [g for g, e in locations.evaluate.items() if e]

    def prepare(self) -> ComputationalSpace:
        """Instantiates :class:`~.ComputationalSpace` instance.

        Generates a :class:`~.ComputationalSpace` instance from
        :attr:`settings`. 

        Returns
        -------
        :class:`~.ComputationalSpace`
            The Computational Space created from :attr:`settings`. 
        """
        print("Preparing Eddy Diffusion run...")
        restrict = {"models": "eddy_diffusion"}
        return ComputationalSpace(self.settings, restrict)
    
    def evaluate(self) -> None:
        """Loops over all elements in :attr:`space` and evaluates the model.

        Returns
        -------
        None

        """
        for setting in self.space.space:
            count = f"{self.space.linear_index(setting) + 1}/{len(self.space)}"
            print(f"Evaluating computational space element {count}")
            self.run(setting)

    def run(self, setting: RIDTConfig) -> None:
        """Evaluates the model for a set of parameters, for all geometries.
    
        Loops over all monitor locations that have been selected for evaluation
        and evaluates them over their respective domains. Writes output to
        :attr:`data_store`.

        Parameters
        ----------
        settings : :class:`~.RIDTConfig`
            The settings for the run in question.

        Returns
        -------
        None

        """
        self.data_store.add_run(setting)

        domain = Domain(setting)
        solver = EddyDiffusion(setting)
        locations = setting.models.eddy_diffusion.monitor_locations

        for geometry in self.geometries:
            print(f"Evaluating {geometry} monitor locations...")
            for name, item in getattr(locations, geometry).items():
                print(f"Evaluating {name}...")
                space = getattr(domain, geometry)(item)
                output = solver(*getattr(domain, geometry)(item), domain.time)
                self.data_store[setting].add(geometry, name, squeeze(output))
    
    def compute_exposure(self) -> None:
        """Computes the exposure from the concentration data.

        Saves the result to a new data store :attr:`exposure_store`

        Returns
        -------
        None

        """
        if self.settings.compute_exposure:
            print("\nComputing exposure...")
            self.exposure_store = Exposure(self.settings, self.data_store)

    def args(self, data_store: BatchDataStore, quantity: str) -> tuple:
        """A helper function that returns a tuple of some values.

        Parameters
        ----------

        data_store : :class:`~.BatchDataStore`
            A batch data store.

        quantity : :obj:`str`
            The name of the quantity in the data store.

        Returns
        -------
        :obj:`tuple`
            The various quantites as a tuple.

        """
        return self.settings, data_store, self.space, self.outdir, quantity

    def write(self) -> None:
        """Writes all data stores to disk.

        Returns
        -------
        None

        """
        print("\nWriting data to disk... ")
        BatchDataStoreWriter(*self.args(self.data_store, "concentration"))
        if self.settings.compute_exposure:
            BatchDataStoreWriter(*self.args(self.exposure_store, "exposure"))


    def plot(self) -> None:
        """Plots all requested data and writes it to disk.

        Returns
        -------
        None

        """
        print("\nProducing plots... ")
        BatchDataStorePlotter(*self.args(self.data_store, "concentration"))
        if self.settings.compute_exposure:
            BatchDataStorePlotter(*self.args(self.exposure_store, "exposure"))

    def analyse(self) -> None:
        """Performs all relevant analysis and writes it to disk.

        Returns
        -------
        None

        """
        if not self.settings.models.eddy_diffusion.analysis.perform_analysis:
            return
        print("\nPerforming data ananlysis...")
        BatchDataStoreAnalyser(*self.args(self.data_store, "concentration"))
        if self.settings.compute_exposure:
            BatchDataStoreAnalyser(*self.args(self.exposure_store, "exposure"))

