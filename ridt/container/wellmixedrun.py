from multiprocessing import Manager
from multiprocessing import Pool
from multiprocessing.managers import DictProxy

from ridt.base import ComputationalSpace
from ridt.equation import WellMixed

from ridt.config import RIDTConfig

from ridt.data import BatchDataStore
from ridt.data import BatchDataStoreWriter
from ridt.data import BatchDataStorePlotter

from ridt.analysis import Exposure

from ridt.container import Domain


BF = '{l_bar}{bar:30}{r_bar}{bar:-10b}'


def run(setting: RIDTConfig, data_store: DictProxy) -> None:
        """Evaluates the model for a set of parameters.

        Writes output to :attr:`data_store`.

        Parameters
        ----------
        settings : :class:`~.RIDTConfig`
            The settings for the run in question.

        Returns
        -------
        None

        """
        domain = Domain(setting)
        solver = WellMixed(setting)
        output = solver(domain.time)
        data_store[setting].add("points", "well_mixed", output)


class WellMixedRun:
    """The class which orchestrates an Well Mixed model run.

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
    def __init__(self, settings: RIDTConfig, output_dir: str):
        """The constructor for the :class:`EddyDiffusion` class.

        Parameters
        ----------
        settings : :class:`~.RIDTConfig`
            The settings for the run in question.

        outdir : :obj:`str`
            The path to the output directory for the run.

        """
        self.settings = settings
        self.outdir = output_dir
        self.manager = Manager()
        self.data_store = BatchDataStore(self.manager)
        self.exposure_store = None
        self.space = self.prepare()
        self.evaluate()
        self.compute_exposure()
        self.write()
        self.plot()
        print("\n")

    def prepare(self) -> ComputationalSpace:
        """Instantiates :class:`~.ComputationalSpace` instance.

        Generates a :class:`~.ComputationalSpace` instance from
        :attr:`settings`. 

        Returns
        -------
        :class:`~.ComputationalSpace`
            The Computational Space created from :attr:`settings`. 
        """
        print("Preparing Well Mixed run... ")
        restrict = {"models": "well_mixed"}
        return ComputationalSpace(self.settings, restrict)
    
    def evaluate(self) -> None:
        """Loops over all elements in :attr:`space` and evaluates the model.

        Returns
        -------
        None

        """
        print("Evaluating model over domain... ")
        count = 4
        inp = []
        for item in self.space.space:
            self.data_store.add_run(item)
            inp.append((item, self.data_store.store))
        with Pool(processes=4) as pool:
            pool.starmap(run, inp)
        # for setting in self.space.space:
        #     count = f"{self.space.linear_index(setting) + 1}/{len(self.space)}"
        #     print(f"Evaluating computational space element {count}")
        #     self.run(setting)
        # for setting in self.space.space:
        #     count = f"{self.space.linear_index(setting) + 1}/{len(self.space)}"
        #     print(f"Evaluating computational space element {count}")
        #     self.run(setting)

    def run(self, setting: RIDTConfig) -> None:
        """Evaluates the model for a set of parameters.

        Writes output to :attr:`data_store`.

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
        solver = WellMixed(setting)
        output = solver(domain.time)
        self.data_store[setting].add("points", "well_mixed", output)

    def compute_exposure(self):
        """Computes the exposure from the concentration data.

        Saves the result to a new data store :attr:`exposure_store`

        Returns
        -------
        None

        """
        if self.settings.compute_exposure:
            print("Computing exposure...")
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
            The various quantities as a tuple.

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
