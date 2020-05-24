import sys
import click

from config.configfileparser import ConfigFileParser
from config.configfileparser import ConfigFileParserJSONError
from config.configfileparser import ConfigFileParserOSError
from config.configfileparser import ConfigFileParserValidationError
from config.csvtoconfigfile import CSVToConfigFile
from container.wellmixedrun import WellMixedRun
from container.eddydiffusionrun import EddyDiffusionRun
from base.settings import ComputationalSpace

@click.group()
def idmf():
    pass



@idmf.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path(exists=True))
def run(config_file, output_dir):
    """Run one or several config files and write all data to the given directory."""
    try:
        with ConfigFileParser() as cfp:
            s = cfp(config_file)
    except (ConfigFileParserJSONError,
            ConfigFileParserOSError,
            ConfigFileParserValidationError) as e:
        sys.exit(e)

    if s.dispersion_model == "well_mixed":
        r = WellMixedRun(s, output_dir)

    if s.dispersion_model == "eddy_diffusion":
        EddyDiffusionRun(s, output_dir)


@idmf.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('-o', '--output_file', type=click.Path())
@click.option('--force/--no-force', default=False)
def csv_to_config(config_file, csv_file, output_file, force):
    if config_file == output_file:
        if not force:
            sys.exit("To overwrite the original config file, use the --force"
                     " flag.")
    with CSVToConfigFile() as ctc:
        ctc(config_file, csv_file, output_file)

    pass

if __name__ == '__main__':
    idmf()