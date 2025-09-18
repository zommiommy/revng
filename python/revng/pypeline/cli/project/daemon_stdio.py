#
# This file is distributed under the MIT License. See LICENSE.md for details.
#

import sys
import json
import logging

import click
import uvicorn
import yaml

import revng
from revng.pypeline.daemon.app import app
from revng.pypeline.daemon.daemon import Daemon
from revng.pypeline.daemon.lock.local_lock import LocalLock

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode.",
)
@click.option(
    "--lock",
    type=click.Choice(["local"]),
    default="local",
    help="The lock type to use.",
    show_default=True,
)
@click.pass_context
def run_daemon(ctx, debug, lock):
    """Start the stdin-stdout-daemon."""
    lock_ty = {
        "local": LocalLock,
    }[lock]

    with open(ctx.obj["pipeline_path"], "r", encoding="utf-8") as f:
        pipeline_yaml = yaml.safe_load(f.read())

    daemon = Daemon(
        version=revng.__version__,
        pipeline_yaml=pipeline_yaml,
        pipeline=ctx.obj["pipeline"],
        debug=debug,
        lock=lock_ty(),
        storage_provider_url=ctx.obj["storage_provider"],
        cache_dir=ctx.obj["cache_dir"],
    )

    while True:
        # Incrementally parse json objects
        in_data = json.load(sys.stdin)

        # TODO:  validate

        if in_data["route"] == "epoch":
            response = daemon.get_epoch()


        json.dump(response.to_dict(), sys.stdout)
        sys.stdout.flush()
