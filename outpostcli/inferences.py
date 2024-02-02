import click
from outpostcli.config_utils import (
    get_default_api_token_from_config,
    get_default_entity_from_config,
)
from outpostcli.utils import click_group
from outpostkit import Client
from outpostkit.inference import Inferences
from rich.table import Table


@click_group()
def inferences():
    """
    Manage Inferences
    """
    pass


@inferences.command(name="list")
@click.option("--api-token", "-t", default=lambda: get_default_api_token_from_config())
@click.option("--entity", "-e", default=lambda: get_default_entity_from_config())
def list_inferences(api_token, entity):
    client = Client(api_token=api_token)
    infs = Inferences(client=client, entity=entity).list
    inf_table = Table(
        title=f"Inference Services ({infs['total']})",
    )
    click.echo(infs)
    # "primary_endpoint",
    cols = ["id", "fullName", "createdAt", "status", "load"]
