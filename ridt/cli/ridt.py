import sys

import shutil

from os.path import isdir
from os.path import join
from os.path import dirname
from os import getcwd
from os import listdir


import click

from ridt.base import ConsistencyError
from ridt.config.configfileparser import ConfigFileParser
from ridt.config.configfileparser import ConfigFileParserJSONError
from ridt.config.configfileparser import ConfigFileParserOSError
from ridt.config.configfileparser import ConfigFileParserValidationError
from ridt.config.csvtoconfigfile import CSVToConfigFile
from ridt.container.wellmixedrun import WellMixedRun
from ridt.container.eddydiffusionrun import EddyDiffusionRun
from ridt.base import RIDTOSError

@click.group()
def ridt():
    """The rapid indoor diffusion tool (ridt)."""
    pass

@ridt.command()
def init():
    """Copy a default config file to current working directory.

    """
    try:
        source_path = join(dirname(__file__), "..", "default")
        for item in listdir(source_path):
            s = join(source_path, item)
            d = join(getcwd(), item)
            if isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
    except OSError as e:
        print(f"Could not clone default config file. Error: {e}")


@ridt.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path(exists=True))
def run(config_file, output_dir):
    """Run diffusion model."""

    if not isdir(output_dir):
        sys.exit(f"{output_dir} is not a directory.\n\nAborted.")

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


@ridt.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('-o', '--output_file', type=click.Path())
@click.option('--force/--no-force', default=False)
def csv_to_config(config_file, csv_file, output_file, force):
    """Merge CSV file to config JSON file. """
    if config_file == output_file:
        if not force:
            sys.exit("To overwrite the original config file, use the --force"
                     " flag.")
    with CSVToConfigFile() as ctc:
        ctc(config_file, csv_file, output_file)

    pass
