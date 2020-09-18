# ridt

RIDT (rapid indoor dispersion tool) is a Python implementation of two different
analytical dispersion models, Eddy Diffusion and Well Mixed. It allows the
calculation of concentrations and exposures based on an arbitrary set of
instantaneous, infinite duration, and fixed duration source terms in a cuboid
bounded system. The Well Mixed model is a set of dimensionless exponential decay
equations, whereas the Eddy Diffusion model is a variant of the standard
solution to the 1D diffusion equation solved with closed boundary conditions,
combined in a separable product in three dimensions.

# Getting Started

## Windows
1. Install Python 3.8.x.

   * The installer can be found [here](https://www.python.org/downloads/release/python-380/).

   * Once you have installed it to some location *path*, add both *path* and
     *path*/Scripts to your system path. For instructions of how to add things
     to your system path, please see
     [here](https://answers.microsoft.com/en-us/windows/forum/windows_10-other_settings/adding-path-variable/97300613-20cb-4d85-8d0e-cc9d3549ba23).
   
   * If you open a Command Prompt or Powershell window and type `python -V` you
   should see Python 3.8.x, where x is the subversion of Python 3.8 you
   downloaded.

   * You should also have access to the Python package manager pip. If you run
     the command `pip`, you should see usage instructions appear. 

2. Install ridt.

   * If you have pip installed, you can simply run the command `pip install ridt`
     to install the latest version of ridt.

# Usage
Please refer to the comprehensive [user guide](https://github.com/riskaware-ltd/ridt/blob/master/user_guide/user_guide.pdf).