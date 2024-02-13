import json

import click
from outpostkit import Client, Endpoint
from outpostkit.utils import convert_outpost_date_str_to_date
from rich.table import Table

from outpostcli.utils import (
    add_options,
    api_token_opt,
    click_group,
    console,
    entity_opt,
)


@click_group()
def inference():
    """
    Manage an Inference service
    """
    pass


@inference.command(name="get")
@add_options([api_token_opt, entity_opt])
@click.argument("name", type=str, nargs=1)
def get_inference(api_token, entity, name):
    client = Client(api_token=api_token)
    inf_data = Endpoint(client=client, name=name, entity=entity).get()
    click.echo(inf_data.__dict__)


@inference.command(name="deploy")
@click.argument("name", type=str, nargs=1)
@add_options([api_token_opt, entity_opt])
def deploy_inference(api_token, entity, name):
    client = Client(api_token=api_token)
    deploy_data = Endpoint(client=client, name=name, entity=entity).deploy({})
    click.echo(f"Deployment successful. id: {deploy_data.id}")


@inference.command(name="deployments")
@add_options([api_token_opt, entity_opt])
@click.argument("name", type=str, nargs=1)
def list_inference_deployments(api_token, entity, name):
    client = Client(api_token=api_token)
    deployments_resp = Endpoint(
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
@add_options([api_token_opt, entity_opt])
def delete_inference(api_token, entity, name):
    fullName = f"{entity}/{name}"
    if click.confirm(
        f"do you really want to delete this endpoint: {fullName} ?", abort=True
    ):
        client = Client(api_token=api_token)
        delete_resp = Endpoint(client=client, name=name, entity=entity).delete()
        return "Inference endpoint deleted."

    return "Aborted"


@inference.command(name="dep-status")
@click.argument("name", type=str, nargs=1)
@add_options([api_token_opt, entity_opt])
@click.option("--verbose", "-v", is_flag=True, help="Verbose")
def inf_dep_status(api_token, entity, name):
    client = Client(api_token=api_token)
    status_data = Endpoint(
        client=client, api_token=api_token, name=name, entity=entity
    ).status()
    click.echo(status_data)
