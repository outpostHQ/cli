import click
from outpostkit import Client
from outpostkit.inference import Inferences
from outpostkit.utils import convert_outpost_date_str_to_date
from rich.table import Table

from outpostcli.config_utils import (
    get_default_api_token_from_config,
    get_default_entity_from_config,
)
from outpostcli.exceptions import SourceNotSupportedError
from outpostcli.utils import click_group, combine_inf_load_source_model, console


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
    infs_resp = Inferences(client=client, entity=entity).list()
    inf_table = Table(
        title=f"Inference Services ({infs_resp.total})",
    )
    # "primary_endpoint",
    inf_table.add_column("name")
    inf_table.add_column("model")
    inf_table.add_column("status")
    inf_table.add_column("hardware_instance")
    inf_table.add_column("visibility")
    inf_table.add_column("updated_at", justify="right")
    for inf in infs_resp.inferences:
        inf_table.add_row(
            inf.name,
            combine_inf_load_source_model(
                inf.loadModelWeightsFrom, inf.outpostModel, inf.huggingfaceModel
            ),
            inf.status,
            inf.hardwareInstance.name,
            inf.visibility,
            convert_outpost_date_str_to_date(inf.updatedAt).isoformat(),
        )

    console.print(inf_table)


@inferences.command(name="create")
@click.argument("model", type=str, nargs=1)
@click.option("--api-token", "-t", default=lambda: get_default_api_token_from_config())
@click.option("--entity", "-e", default=lambda: get_default_entity_from_config())
@click.option(
    "--revision", "-r", type=str, default=None, help="revision of the model to use."
)
@click.option(
    "--name",
    "-n",
    type=str,
    default=None,
    help="name of the inference endpoint to create.",
)
@click.option(
    "--huggingface-token-id",
    type=str,
    default=None,
    help="revision of the model to use.",
)
@click.option(
    "--hardware-instance",
    "-h",
    type=str,
    help="hardware instance type to use",
)
def create_inference(
    api_token, entity, model, revision, hardware_instance, huggingface_token_id, name
):
    client = Client(api_token=api_token)
    m_splits = model.split(":", 1)
    model_details: dict[str] = None
    if len(m_splits) == 1:
        model_details = {
            "loadModelWeightsFrom": "outpost",
            "outpostModel": {"fullName": model, "commit": revision},
        }
    else:
        if m_splits[0] == "hf" or m_splits[0] == "huggingface":
            model_details = {
                "loadModelWeightsFrom": "huggingface",
                "huggingfaceModel": {"id": m_splits[1], "revision": revision},
                "keyId": huggingface_token_id,
            }
        else:
            raise SourceNotSupportedError(f"source {m_splits[0]} not supported.")
    create_body = {
        **model_details,
        "hardwareInstance": hardware_instance,
        "name": name,
    }
    click.echo(create_body)
    create_resp = Inferences(client=client, entity=entity).create(data=create_body)
    click.echo("Inference created...")
    click.echo(f"name: {create_resp.name}")
    click.echo(f"id: {create_resp.id}")
