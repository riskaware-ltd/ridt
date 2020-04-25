import click

from config.configfileparser import ConfigFileParser

@click.command()
@click.argument('config_file', type=click.Path(exists=True), nargs=-1)
@click.argument('output_dir', type=click.Path(exists=True), nargs=1)
def idmf(config_file, output_dir):
    """Run one or several config files and write all data to the given directory."""
    with ConfigFileParser() as cfp:
        f = cfp(config_file)

if __name__ == '__main__':
    idmf()