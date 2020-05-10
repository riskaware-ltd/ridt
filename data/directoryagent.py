from os import mkdir

from os.path import join

from numpy import unravel_index

class DirectoryAgent:
    
    def __init__(self, outdir: str, shape: tuple):
        self.outdir = outdir
        self.shape = shape
    
    def create_rundir(self, run_idx: tuple):
        try:
            mkdir(self.build_rundir_path(run_idx))
        except OSError as e:
            if isinstance(e, FileExistsError):
                pass
            else:
                # TODO Handle these OSErrors properly.
                raise e
    
    def build_rundir_path(self, run_idx: tuple) -> str:
        idx = unravel_index(run_idx, self.shape)
        return join(self.outdir, str(idx).replace("(","[").replace(")", "]"))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
