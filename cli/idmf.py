import sys
from os.path import isdir
import click

from base import ConsistencyError
from config.configfileparser import ConfigFileParser
from config.configfileparser import ConfigFileParserJSONError
from config.configfileparser import ConfigFileParserOSError
from config.configfileparser import ConfigFileParserValidationError
from config.csvtoconfigfile import CSVToConfigFile
from container.wellmixedrun import WellMixedRun
from container.eddydiffusionrun import EddyDiffusionRun
from base.settings import ComputationalSpace
from base import RIDTOSError

@click.group()
def idmf():
    """The indoor diffusion modelling framework entry point."""
    pass

@idmf.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path(exists=True))
def run(config_file, output_dir):
    if not isdir(output_dir):
        sys.exit(f"{output_dir} is not a directory.\n\nAborted.")

    """Run one or several config files and write all data to the given directory."""
    try:
        s = ConfigFileParser(config_file)
    except (ConfigFileParserJSONError,
            ConfigFileParserOSError,
            ConfigFileParserValidationError) as e:
        sys.exit(e)
    except ConsistencyError as e:
        sys.exit(e)

    try:
        if s.well_mixed:
            WellMixedRun(s, output_dir)
        if s.eddy_diffusion:
            EddyDiffusionRun(s, output_dir)
    except RIDTOSError as e:
        sys.exit(f"\n{e}\n\nAborted.")
    
    print("\nComplete.")


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
