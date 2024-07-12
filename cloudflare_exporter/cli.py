# -*- coding: utf-8 -*-

"""Console script for cloudflare_exporter."""
import sys
import yaml
import click
import logging
import logging.config
from .cloudflare_exporter import run_exporter

# logging
with open("logging.yaml", "r") as f:
    log_cfg = yaml.safe_load(f.read())
    logging.config.dictConfig(log_cfg)
    LOGGER = logging.getLogger("stdout")


@click.group()
@click.option("--debug/--no-debug", default=False)
def main(debug):
    """Console script for cloudflare_exporter."""
    LOGGER.debug(
        f"Running cloudflare_exporter in %s mode" % ("debug" if debug else "standard")
    )


@main.command()
@click.argument("config", type=click.File("rb"))
def export(config):
    LOGGER.debug("parallel export mode")
    config_dict = yaml.load(config, Loader=yaml.FullLoader)
    run_exporter(config_dict)


@main.command()
def get():
    LOGGER.debug("get mode")


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
