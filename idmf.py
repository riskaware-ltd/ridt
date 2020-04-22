import click


@click.command()
@click.argument('config_file', type=click.Path(exists=True), help='The path to the configuration file.', nargs=-1)
@click.argument('output_dir', type=click.Path(exists=True), help='The path to the output directory.', nargs=1)
def idmf(config_file, output_dir):
    """Run one or several config files and write all data to the given directory."""
    pass
