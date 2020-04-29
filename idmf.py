import sys
import click
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import numpy as np

from config.configfileparser import ConfigFileParser
from config.configfileparser import ConfigFileParserJSONError
from config.configfileparser import ConfigFileParserOSError
from config.configfileparser import ConfigFileParserValidationError
from container.wellmixedrun import WellMixedRun
from equation.eddy_diffusion import EddyDiffusion


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

    if s.dispersion_model == "well_mixed":
        WellMixedRun(s)

    x = s.models.eddy_diffusion.dimensions.x
    y = s.models.eddy_diffusion.dimensions.y
    z = s.models.eddy_diffusion.dimensions.z
    t = s.total_time
    x_range = np.linspace(
        0, x, s.spatial_samples)
    y_range = np.linspace(
        0, y, s.spatial_samples)
    z_range = np.linspace(
        0, z, s.spatial_samples)
    t_range = np.linspace(
        1, t, s.time_samples)
    tt, xx, yy, zz = np.meshgrid(t_range, x_range, y_range, z_range, indexing="ij")

    e = EddyDiffusion(s) 
    out = e(xx, yy, zz, tt)

    x = np.linspace(0, s.models.eddy_diffusion.dimensions.x, s.spatial_samples)
    y = np.linspace(0, s.models.eddy_diffusion.dimensions.y, s.spatial_samples)
    fig = plt.figure()
    ax = plt.axes(xlim=(0, s.models.eddy_diffusion.dimensions.x), ylim=(0, s.models.eddy_diffusion.dimensions.y), xlabel='x', ylabel='y')
    def get_slice(i):
        return out[i, :, :, int(s.spatial_samples / 2)]
    plot = plt.contourf(x, y, get_slice(0))
    plt.colorbar()
    def animate(i):
        plt.title(f"{i}")
        return plt.contourf(x, y, get_slice(i))
    anim = animation.FuncAnimation(fig, animate, frames=100, repeat=True)
    plt.show()

if __name__ == '__main__':
    idmf()