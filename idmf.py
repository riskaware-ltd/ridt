import sys
import click

from config.configfileparser import ConfigFileParser
from config.configfileparser import ConfigFileParserJSONError
from config.configfileparser import ConfigFileParserOSError
from config.configfileparser import ConfigFileParserValidationError
from container.wellmixedrun import WellMixedRun


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

if __name__ == '__main__':
    idmf()