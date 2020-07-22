from os.path import join

from numpy import save

from ridt.config import RIDTConfig
from ridt.config import ConfigFileWriter

from .directoryagent import DirectoryAgent

from .datastore import DataStore


class DataStoreWriter:
    """A class that attempts to read a data store from disk.

    This will only work if the folder structure generated when writing the data
    store to disk is un modified.

    When creating a new instance of this class, an instance of
    :class:`~.DataStore` or :class:`~.BatchDataStore` will be returned instead
    of :class:`~.DataStoreReader`.

    Attributes
    ----------
    settings : :class:`~.RIDTConfig`
        The settings for the run output stored in the data store.
    
    quantity: :obj:`str`
        The string id for the quantity stored in the data  store.

    dir_agent : :class:`~.DirectoryAgent`
        The path to the output directory for the run.

    """

    def __new__(cls, *args, **kwargs):
        instance = super(DataStoreWriter, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance

    def __init__(self,
                 setting: RIDTConfig,
                 data_store: DataStore,
                 dir_agent: DirectoryAgent,
                 quantity: str):
        """The :class:`~.DataStoreWriter` constructor.

        Parameters
        ----------
        settings : :class:`~.RIDTConfig`
            The settings for the run output stored in the data store.
        
        quantity: :obj:`str`
            The string id for the quantity stored in the data  store.

        dir_agent : :class:`~.DirectoryAgent`
            The path to the output directory for the run.

        data_store : :class:`~.DataStore`
            The data store to be written.

        """
        self.dir_agent = dir_agent
        self.setting = setting
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
        """Method that loop over the entries in the data store and writes them.

        The settings object is converted to JSON and written to disk.

        The :attr:`dir_agent` creates and provides paths to the relevant
        directories.

        Parameters
        ----------
        data_store : :class:`~.DataStore`
            The data store to be written.
        
        Returns
        -------
        None

        """
        ConfigFileWriter(self.dir_agent.outdir, "config.json", self.setting.__source__)
        for geometry in self.geometries:
            self.dir_agent.create_data_dir(geometry, self.quantity)
            for id in getattr(data_store, geometry):
                save(join(self.dir_agent.ddir, id), data_store.get(geometry, id))
