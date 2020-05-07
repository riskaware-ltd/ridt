import sys
import click

from config.configfileparser import ConfigFileParser
from config.configfileparser import ConfigFileParserJSONError
from config.configfileparser import ConfigFileParserOSError
from config.configfileparser import ConfigFileParserValidationError
from container.wellmixedrun import WellMixedRun
from container.eddydiffusionrun import EddyDiffusionRun


@click.command()
@click.argument('config_file', type=click.Path(exists=True))
def idmf(config_file):
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
        WellMixedRun(s)

    if s.dispersion_model == "eddy_diffusion":
        EddyDiffusionRun(s)


if __name__ == '__main__':
    idmf()