from os import mkdir

from os.path import join

from numpy import unravel_index

from ridt.base import RIDTOSError

class DirectoryAgent:
    """This class provides directory creation functionality.

    This class provides various methods for creating nested directory structures
    required to store the raw binary grids, csv files, analysis, and plots.

    Attributes
    ----------
    rootdir : :obj:`str`
        The main directory where everything is stored.

    outdir : :obj:`str`
        The the current root dir for a given computational space index.

    gdir: :obj:`str`
        The the current geometry dir relative to the :attr:`rootdir`.
    
    qdir : :obj:`str`
        The current quantitiy dir relative to the :attr:`gdir`.
    
    ddir : :obj:`str`
        The current data dir relative to the :attr:`qdir`.

    pdir : :obj:`str`
        The current plot dir relative to the :attr:`qdir`.
    
    adir : :obj:`str`
        The current analysis dir relative to the :attr:`qdir`.
    
    shape : :obj:`Tuple`[:obj:`int`]
        The shape of the computational space.

    """
    
    def __init__(self, outdir: str, shape: tuple):
        """The :class:`~.DirectoryAgent` constructor.

        Parameters
        ----------


        """
        self.shape = shape
        self.rootdir = outdir
        self.outdir = outdir
        self.gdir = None
        self.qdir = None
        self.ddir = None
        self.pdir = None
        self.adir = None
    
    def create_root_dir(self, run_idx: tuple) -> None:
        """Create the subdirectory for a batch run element.

        Parameters
        ----------
        run_idx : :obj:`Tuple`[:obj:`int`]
            The index in computational space of the run.
        
        Returns
        -------
        None

        """
        idx = unravel_index(run_idx, self.shape)
        idx = str(idx).replace("(","[").replace(")", "]")
        self.outdir = join(self.rootdir, idx)
        self.mkdir(self.outdir)
   
    def create_geometry_dir(self, geometry: str):
        """Create the geometry subdirectory.

        Parameters
        ----------
        geometry : :obj:`str`
            The name of the geometry class.

        Returns
        -------
        :obj:`str`
            The path to the new directory.

        """
        self.gdir = join(self.outdir, geometry)
        self.mkdir(self.gdir)
        return self.gdir

    def create_quantity_dir(self, geometry: str, quantity: str):
        """Create the quantity subdirectory.

        Parameters
        ----------
        geometry : :obj:`str`
            The name of the geometry class.
        
        quantity : :obj:`str`
            The string id of the quantity.  

        Returns
        -------
        :obj:`str`
            The path to the new directory.

        """
        self.create_geometry_dir(geometry)
        self.qdir = join(self.gdir, quantity)
        self.mkdir(self.qdir)
        return self.qdir
    
    def create_data_dir(self, geometry: str, quantity: str):
        """Create the data subdirectory.

        Parameters
        ----------
        geometry : :obj:`str`
            The name of the geometry class.
        
        quantity : :obj:`str`
            The string id of the quantity.  

        Returns
        -------
        :obj:`str`
            The path to the new directory.

        """
        self.create_quantity_dir(geometry, quantity)
        self.ddir = join(self.qdir, "data")
        self.mkdir(self.ddir)
        return self.ddir
    
    def create_plot_dir(self, geometry: str, quantity: str):
        """Create the plots subdirectory.

        Parameters
        ----------
        geometry : :obj:`str`
            The name of the geometry class.
        
        quantity : :obj:`str`
            The string id of the quantity.  

        Returns
        -------
        :obj:`str`
            The path to the new directory.

        """
        self.create_quantity_dir(geometry, quantity)
        self.pdir = join(self.qdir, "plots")
        self.mkdir(self.pdir)
        return self.pdir
    
    def create_analysis_dir(self, geometry: str, quantity: str):
        """Create the analysis subdirectory.

        Parameters
        ----------
        geometry : :obj:`str`
            The name of the geometry class.
        
        quantity : :obj:`str`
            The string id of the quantity.  

        Returns
        -------
        :obj:`str`
            The path to the new directory.

        """
        self.create_quantity_dir(geometry, quantity)
        self.adir = join(self.qdir, "analysis")
        self.mkdir(self.adir)
        return self.adir

    def mkdir(self, path: str) -> None:
        """Create a directory at the provided path.

        Parameters
        ----------
        path : :obj:`str`
            The path to the new directory.
        
        Returns
        -------
        None

        Raises
        ------
        :class:`~.RIDTOSError`
            If cannot create the new directory.

        """
        try:
            mkdir(path)
        except FileExistsError:
            pass
        except OSError as e:
            raise RIDTOSError(e)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
