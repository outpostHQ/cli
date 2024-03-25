# ref: https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/commands/lfs.py
import json
import os
import subprocess
import sys
from argparse import _SubParsersAction
from typing import Dict, List, Optional

import click
from huggingface_hub.commands import BaseHuggingfaceCLICommand
from huggingface_hub.lfs import LFS_MULTIPART_UPLOAD_COMMAND, SliceFileObj
from ..utils import get_session, hf_raise_for_status, logging

logger = logging.get_logger(__name__)


@click.group()
def cli():
    pass


class LfsCommands(BaseHuggingfaceCLICommand):
    @staticmethod
    def register_subcommand(parser: _SubParsersAction):
        parser.add_command(enable_largefiles)
        parser.add_command(multipart_upload)


@click.command()
@click.argument("path", type=str)
def enable_largefiles(path):
    """Configure your repository to enable upload of files > 5GB."""
    local_path = os.path.abspath(path)
    if not os.path.isdir(local_path):
        click.echo("This does not look like a valid git repo.")
        sys.exit(1)
    subprocess.run(
        "git config lfs.customtransfer.multipart.path huggingface-cli".split(),
        check=True,
        cwd=local_path,
    )
    subprocess.run(
        f"git config lfs.customtransfer.multipart.args {LFS_MULTIPART_UPLOAD_COMMAND}".split(),
        check=True,
        cwd=local_path,
    )
    click.echo("Local repo set up for largefiles")


@click.command()
def multipart_upload():
    """Command called by lfs directly and is not meant to be called by the user."""
    # ... (rest of the existing code)


if __name__ == "__main__":
    cli()
