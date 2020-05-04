import sys
import click
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LogNorm
from matplotlib import ticker
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})


import numpy as np

from config.configfileparser import ConfigFileParser
from config.configfileparser import ConfigFileParserJSONError
from config.configfileparser import ConfigFileParserOSError
from config.configfileparser import ConfigFileParserValidationError
from container.wellmixedrun import WellMixedRun
from container.eddydiffusionrun import EddyDiffusionRun 
from equation.eddy_diffusion import EddyDiffusion
from equation.well_mixed import WellMixed 


@click.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path(exists=True))
def idmf(config_file, output_dir):
    """Run one or several config files and write all data to the given directory."""
    try:
        with ConfigFileParser() as cfp:
            s = cfp(config_file)
    except (ConfigFileParserJSONError,
            ConfigFileParserOSError,
            ConfigFileParserValidationError) as e:
        sys.exit(e)

    s.consistency_check()

    if s.dispersion_model == "well_mixed":
        t = s.total_time
        t_range = np.linspace(1e-3, t, s.time_samples)
        e = WellMixed(s)
        val = e(t_range)
        plt.xlabel("time (s)")
        plt.ylabel("Concentration $(kgm^-3)$")
        plt.tight_layout()
        plt.plot(t_range, val)
        plt.savefig("infinite")

    if s.dispersion_model == "eddy_diffusion":
        x = s.models.eddy_diffusion.dimensions.x
        y = s.models.eddy_diffusion.dimensions.y
        z = s.models.eddy_diffusion.dimensions.z
        t = s.total_time
        x_range = np.linspace(0, x, s.models.eddy_diffusion.spatial_samples.x)
        y_range = np.linspace(0, y, s.models.eddy_diffusion.spatial_samples.y)
        z_range = np.linspace(0, z, s.models.eddy_diffusion.spatial_samples.z)
        t_range = np.linspace(1e-3, t, s.time_samples)
        xx, yy, zz = np.meshgrid(x_range, y_range, z_range, indexing="ij")

        s.consistency_check()
        e = EddyDiffusion(s) 
        out = e(xx, yy, zz, t_range)

        fig = plt.figure()
        ax = plt.axes(xlim=(0, s.models.eddy_diffusion.dimensions.x), ylim=(0, s.models.eddy_diffusion.dimensions.y), xlabel='x', ylabel='y')
        def get_slice(i):
            return out[i, :, :, int(s.models.eddy_diffusion.spatial_samples.z / 2)]
        levels = [1e-5, 5e-5, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 1e-1, 5e-1, 1, 5, 1e1, 5e1, 1e2]

        plot = plt.contourf(x_range, y_range, get_slice(0), levels, cmap=plt.cm.summer, norm=LogNorm(), extend='min')
        plot.cmap.set_under("black")
        plt.colorbar()
        def animate(i):
            plt.title(f"{i}")
            plot = plt.contourf(x_range, y_range, get_slice(i), levels, cmap=plt.cm.summer, norm=LogNorm(), extend='min')
            plot.cmap.set_under("black")
            return plot
        anim = animation.FuncAnimation(fig, animate, frames=s.time_samples, repeat=True)
        plt.show()

if __name__ == '__main__':
    idmf()