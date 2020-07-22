import csv

from itertools import product

from os.path import join

from tqdm import tqdm

from numpy import ndarray

from ridt.base import RIDTOSError

from ridt.config import RIDTConfig
from ridt.config import Units

from .directoryagent import DirectoryAgent

from ridt.container import Domain

from .datastore import DataStore

from ridt import bar_args


class DataStoreCSVWriter:
    """Class that writes a :class:`~.DataStore` instance to CSV files.

    Attributes
    ----------
    settings : :class:`~.RIDTConfig`
        The settings for the run in question.

    dir_agent : :class:`~.DirectoryAgent`
        The path to the output directory for the run.
    
    domain : :class:`~.Domain`
        The instance of :class:`~.Domain` corresponding to :attr:`setting`.

    units : :class:`~.Units`
        The instance of :class:`~.Units` corresponding to :attr:`setting`.

    data_store : :class:`~.DataStore`
        The data store to be analysed.

    quantity: :obj:`str`
        The string id for the quantity stored in the data  store.

    """ 

    def __init__(self,
                 setting: RIDTConfig,
                 data_store: DataStore,
                 dir_agent: DirectoryAgent,
                 quantity: str):
        """The :class:`DataStoreCSVWriter` constructor.

        Parameters
        ----------
        settings : :class:`~.RIDTConfig`
            The settings for the run in question.

        dir_agent : :class:`~.DirectoryAgent`
            The path to the output directory for the run.
        
        data_store : :class:`~.DataStore`
            The data store to be analysed.

        quantity: :obj:`str`
            The string id for the quantity stored in the data  store.

        """
        self.dir_agent = dir_agent
        self.setting = setting
        self.units = Units(setting)
        self.domain = Domain(setting)
        self.quantity = quantity
        self.write(data_store)
    
    @property
    def geometries(self):
        """:obj:`list` [:obj:`str`] : the list of geometries selected for
        evaluation in :attr:`settings`.

        """
        locations = self.setting.models.eddy_diffusion.monitor_locations
        return [g for g, e in locations.evaluate.items() if e]

    def write(self, data_store: DataStore) -> None:
        """Loops over entries in the data store and writes the data to csv file.

        Parameters
        ----------
        data_store : :class:`~.DataStore`
            The data store to be analysed.
        
        Returns
        -------
        None

        """
        for geometry in self.geometries:
            self.dir_agent.create_data_dir(geometry, self.quantity)
            for id in getattr(data_store, geometry):
                self.write_csv(geometry, id, data_store.get(geometry, id))
    
    def write_csv(self, geometry: str, id: str, data: ndarray) -> None:
        """Takes string identifiers and the grid and writes them to a csv file.

        Parameters
        ----------
        geometry : :obj:`str`
            The type of grid to be written.

        id : :obj:`str`
            The id of the grid to be written.

        data : :class:`~numpy.ndarray`
            The grid to be written.

        Raises
        ------
        :class:`~.RIDTOSError`
            If unable to create the file on disk.
        
        Returns
        -------
        None

        """
        path = join(self.dir_agent.ddir, id + ".csv")
        factor = getattr(self.units, f"{self.quantity}_factor")

        try:
            f = open(path, 'w', newline="")
        except OSError as e:
            raise RIDTOSError(e)

        writer = csv.writer(f, delimiter=",")
        writer.writerow([
            f"time ({self.units.time})",
            f"x ({self.units.space})",
            f"y ({self.units.space})",
            f"z ({self.units.space})",
            f"value ({getattr(self.units, f'{self.quantity}')})"
        ])

        indices = list(product(*[range(i) for i in data.shape]))

        print(f"Writing {id} {self.quantity} data to a csv file...")
        for index in tqdm(indices, total=len(indices), **bar_args):
            values = self.domain.values(id, index)
            writer.writerow(list(values) + [data[index] / factor])
        f.close()