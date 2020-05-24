from os import mkdir

from os.path import join

from numpy import unravel_index

class DirectoryAgent:
    
    def __init__(self, outdir: str, shape: tuple):
        self.rootdir = outdir
        self.outdir = outdir
        self.shape = shape
    
    def create_root_dir(self, run_idx: tuple):
        idx = unravel_index(run_idx, self.shape)
        idx = str(idx).replace("(","[").replace(")", "]")
        self.outdir = join(self.rootdir, idx)
        self.mkdir(self.outdir)
   
    def create_geometry_dir(self, geometry: str):
        self.gdir = join(self.outdir, geometry)
        self.mkdir(self.gdir)

    def create_quantity_dir(self, geometry: str, quantity: str):
        self.create_geometry_dir(geometry)
        self.qdir = join(self.gdir, quantity)
        self.mkdir(self.qdir)
        return self.qdir

    def mkdir(self, path: str):
        try:
            mkdir(path)
        except FileExistsError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
