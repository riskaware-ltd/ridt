from os.path import join

from numpy import load

from ridt.base import ComputationalSpace
from ridt.base import Error

from ridt.config import ConfigFileParser
from ridt.config import RIDTConfig

from .batchdatastore import BatchDataStore
from .directoryagent import DirectoryAgent
from .datastore import DataStore

class DataStoreReader:
    """A class that attempts to read a data store from disk.

    This will only work if the folder structure generated when writing the data
    store to disk is un modified.

    When creating a new instance of this class, an instance of
    :class:`~.DataStore` or :class:`~.BatchDataStore` will be returned instead
    of :class:`~.DataStoreReader`.

    Attributes
    ----------
    directory: :obj:`str`
        The directory where the data store is located.
    
    settings : :class:`~.RIDTConfig`
        The settings for the run output stored in the data store.
    
    quantity: :obj:`str`
        The string id for the quantity stored in the data  store.

    space : :class:`~.ComputationalSpace`
        The :class:`~.ComputationalSpace` instance corresponding to the
        :attr:`settings` attribute.

    data_store : :obj:`Union`[:class:`~.DataStore`, :class:`~.BatchDataStore`]
        The parsed data store.

    """

    def __new__(cls, *args, **kwargs):
        instance = super(DataStoreReader, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.data_store

    def __init__(self, settings: RIDTConfig, directory: str, quantity: str):
        """The :class:`DataStoreReader` constructor.

        Parameters
        ----------
        directory: :obj:`str`
            The directory where the data store is located.
        
        settings : :class:`~.RIDTConfig`
            The settings for the run output stored in the data store.
        
        quantity: :obj:`str`
            The string id for the quantity stored in the data  store.

        """
        self.directory = directory
        self.settings = settings
        self.quantity = quantity
        restrict = {"models": self.settings.dispersion_model}
        self.space = ComputationalSpace(self.settings, restrict)
        self.read()

    @property
    def geometries(self):
        """:obj:`list` [:obj:`str`] : the list of geometries selected for
        evaluation in :attr:`settings`.

        """
        locations = self.settings.models.eddy_diffusion.monitor_locations
        return [g for g, e in locations.evaluate.items() if e]

    def read(self) -> None:
        """This method attempts to load the data store  .

        If :attr:`settings` is a batch settings object then it will loop over
        all elements in the computational space.

        Returns
        -------
        None


        """
        if self.space.zero:
            self.data_store = self.load(self.settings, self.directory)
        else:
            self.data_store = BatchDataStore()
            with DirectoryAgent(self.directory, self.space.shape) as da:
                for idx, setting in enumerate(self.space.space):
                    da.create_data_dir(idx)
                    self.data_store.add_run(setting)
                    self.data_store[setting] = self.load(setting, da.ddir)
    
    def load(self, setting: RIDTConfig, directory: str):
        """Reads in each numpy array and stores it in the new data store.

        Parameters
        ----------

        settings : :class:`~.RIDTConfig`
            The settings for the run output stored in the data store.

        directory: :obj:`str`
            The directory where the data store is located.

        Returns
        -------
        :class:`~.DataStore`
            The parsed data store.

        Raises
        ------
        :class:`~.DataStoreParsingError`
            If unable to read a numpy binary file from disk.

        """
        rv = DataStore()
        locations = setting.models.eddy_diffusion.monitor_locations

        for geometry in self.geometries:
            for name in getattr(locations, geometry).keys():
                fname = name + ".npy"
                folder = join(directory, geometry, self.quantity)
                try:
                    with open(join(folder, fname), 'rb') as f:
                        rv.add(geometry, name, load(f))
                except OSError as e:
                    raise DataStoreParsingError(fname, folder, e)

        return rv
 

class DataStoreParsingError(Error):
    """The exception raised when an OSError is raised when parsing data arrays
    from disk

    """
    def __init__(self, file_name: str, directory: str, error):
        """The constructor for the :class:`DataStoreParsingError` class.

        """
        msg = f"When loading '{file_name}' from the directory '{directory}'"\
              f" the following error was encoutered: {error}"
        super().__init__(msg)
    