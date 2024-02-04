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
@click.argument("name", type=str, nargs=1)
@click.option("--api-token", "-t", default=lambda: get_default_api_token_from_config())
@click.option("--entity", "-e", default=lambda: get_default_entity_from_config())
@click.option(
    "--revision", "-r", type=str, default=None, help="revision of the model to use."
)
def get_inference(api_token, entity, name):
    client = Client(api_token=api_token)
    inf_data = Inference(
        client=client, api_token=api_token, name=name, entity=entity
    ).get()
    click.echo(inf_data)


@inference.command(name="deploy")
@click.argument("name", type=str, nargs=1)
@click.option("--api-token", "-t", default=lambda: get_default_api_token_from_config())
@click.option("--entity", "-e", default=lambda: get_default_entity_from_config())
def deploy_inference(api_token, entity, name):
    client = Client(api_token=api_token)
    deploy_data = Inference(
        client=client, api_token=api_token, name=name, entity=entity
    ).deploy()
    click.echo(f"Deployment successful. id: {deploy_data.id}")


@inference.command(name="deployments")
@click.argument("name", type=str, nargs=1)
@click.option("--api-token", "-t", default=lambda: get_default_api_token_from_config())
@click.option("--entity", "-e", default=lambda: get_default_entity_from_config())
def list_inference_deployments(api_token, entity, name):
    client = Client(api_token=api_token)
    deployments_resp = Inference(
        client=client, api_token=api_token, name=name, entity=entity
    ).list_deploymets()

    inf_table = Table(
        title=f"Deployments ({deployments_resp.total})",
    )
    # "primary_endpoint",
    inf_table.add_column("id")
    inf_table.add_column("status")
    inf_table.add_column("status")
    inf_table.add_column("concluded_at", justify="right")
    inf_table.add_column("created_at", justify="right")
    for inf in deployments_resp.deployments:
        inf_table.add_row(
            inf.name,
            combine_inf_load_source_model(
                inf.loadModelWeightsFrom, inf.outpostModel, inf.huggingfaceModel
            ),
            inf.status,
            inf.instanceType,
            inf.visibility,
            convert_outpost_date_str_to_date(inf.updatedAt).isoformat(),
        )

    console.print(inf_table)


# @inference.command(name="wake")
# @click.argument("name", type=str, nargs=1)
# @click.option("--api-token", "-t", default=lambda: get_default_api_token_from_config())
# @click.option("--entity", "-e", default=lambda: get_default_entity_from_config())
# def wake(api_token, entity, name):
#     client = Client(api_token=api_token)
#     deploy_data = Inference(
#         client=client, api_token=api_token, name=name, entity=entity
#     ).wake()
#     click.echo(f"Deployment successful. id: {deploy_data.id}")
