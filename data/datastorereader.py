from os.path import join

from numpy import load

from base import ComputationalSpace
from base import Error

from config import ConfigFileParser
from config import IDMFConfig

from .batchdatastore import BatchDataStore
from .directoryagent import DirectoryAgent
from .datastore import DataStore

class DataStoreReader:

    def __new__(cls, *args, **kwargs):
        instance = super(DataStoreReader, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.data_store

    def __init__(self, settings: IDMFConfig, directory: str):
        self.directory = directory
        self.settings = settings
        restrict = {"models": self.settings.dispersion_model}
        self.space = ComputationalSpace(self.settings, restrict)
        self.read()

    def read(self):
        if self.space.zero:
            self.data_store = self.load(self.settings, self.directory)
        else:
            self.data_store = BatchDataStore()
            with DirectoryAgent(self.directory, self.space.shape) as da:
                for idx, setting in enumerate(self.space.space):
                    path = da.build_rundir_path(idx)
                    self.data_store.add_run(setting)
                    self.data_store[setting] = self.load(setting, path)
    
    def load(self, setting: IDMFConfig, directory: str):
        rv = DataStore()
        locations = setting.models.eddy_diffusion.monitor_locations

        for point_name, point in locations.points.items():
            fname = point_name + ".npy"
            try:
                with open(join(directory, fname), 'rb') as f:
                    rv.add_point_data(point_name, load(f))
            except OSError as e:
                raise DataStoreParsingError(fname, directory, e)

        for line_name, line in locations.lines.items():
            fname = line_name + ".npy"
            try:
                with open(join(directory, fname), 'rb') as f:
                    rv.add_line_data(line_name, load(f))
            except OSError as e:
                raise DataStoreParsingError(fname, directory, e)

        for plane_name, plane in locations.planes.items():
            fname = plane_name + ".npy"
            try:
                with open(join(directory, fname), 'rb') as f:
                    rv.add_plane_data(plane_name, load(f))
            except OSError as e:
                raise DataStoreParsingError(fname, directory, e)
        
        fname = "domain" + ".npy"
        try:
            with open(join(directory, "domain" + ".npy"), 'rb') as f:
                rv.add_domain_data(load(f))
        except OSError as e:
            raise DataStoreParsingError(fname, directory, e)
        
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
    