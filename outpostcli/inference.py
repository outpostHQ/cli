import json

import click
from outpostkit import Client
from outpostkit.inference import Inference
from outpostkit.utils import convert_outpost_date_str_to_date
from rich.table import Table

from outpostcli.config_utils import (
    get_default_api_token_from_config,
    get_default_entity_from_config,
)
from outpostcli.exceptions import SourceNotSupportedError
from outpostcli.utils import click_group, combine_inf_load_source_model, console


@click_group()
def inference():
    """
    Manage Inferences
    """
    pass


@inference.command(name="get")
@click.option("--api-token", "-t", default=lambda: get_default_api_token_from_config())
@click.option("--entity", "-e", default=lambda: get_default_entity_from_config())
@click.argument("name", type=str, nargs=1)
def get_inference(api_token, entity, name):
    client = Client(api_token=api_token)
    inf_data = Inference(client=client, name=name, entity=entity).get()
    click.echo(json.dumps(inf_data.__dict__, indent=2))


@inference.command(name="deploy")
@click.argument("name", type=str, nargs=1)
@click.option("--api-token", "-t", default=lambda: get_default_api_token_from_config())
@click.option("--entity", "-e", default=lambda: get_default_entity_from_config())
def deploy_inference(api_token, entity, name):
    client = Client(api_token=api_token)
    deploy_data = Inference(client=client, name=name, entity=entity).deploy({})
    click.echo(f"Deployment successful. id: {deploy_data.id}")


@inference.command(name="deployments")
@click.argument("name", type=str, nargs=1)
@click.option("--api-token", "-t", default=lambda: get_default_api_token_from_config())
@click.option("--entity", "-e", default=lambda: get_default_entity_from_config())
def list_inference_deployments(api_token, entity, name):
    client = Client(api_token=api_token)
    deployments_resp = Inference(
        client=client, name=name, entity=entity
    ).list_deploymets(params={})

    inf_table = Table(
        title=f"Deployments ({deployments_resp.total})",
    )
    # "primary_endpoint",
    inf_table.add_column("id")
    inf_table.add_column("status")
    inf_table.add_column("created_at", justify="right")
    inf_table.add_column("concluded_at", justify="right")
    for inf in deployments_resp.deployments:
        inf_table.add_row(
            inf.id,
            inf.status,
            convert_outpost_date_str_to_date(inf.createdAt).isoformat(),
            (
                convert_outpost_date_str_to_date(inf.concludedAt).isoformat()
                if inf.concludedAt
                else "Not concluded yet."
            ),
        )

    console.print(inf_table)


@inference.command(name="delete")
@click.argument("name", type=str, nargs=1)
@click.option("--api-token", "-t", default=lambda: get_default_api_token_from_config())
@click.option("--entity", "-e", default=lambda: get_default_entity_from_config())
def delete_inference(api_token, entity, name):
    fullName = f"{entity}/{name}"
    if click.confirm(
        f"do you really want to delete this endpoint: {fullName} ?", abort=True
    ):
        client = Client(api_token=api_token)
        delete_resp = Inference(client=client, name=name, entity=entity).delete()
        return "Inference endpoint deleted."

    return "Aborted"


@inference.command(name="dep-status")
@click.argument("name", type=str, nargs=1)
@click.option("--api-token", "-t", default=lambda: get_default_api_token_from_config())
@click.option("--entity", "-e", default=lambda: get_default_entity_from_config())
@click.option("--verbose", "-v", is_flag=True, help="Verbose")
def inf_dep_status(api_token, entity, name):
    client = Client(api_token=api_token)
    # status_data = Inference(
    #     client=client, api_token=api_token, name=name, entity=entity
    # ).status()
    # click.echo()
