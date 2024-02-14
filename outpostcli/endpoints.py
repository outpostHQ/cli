import json
import os
from typing import Optional
from urllib.parse import urlparse

import click
from outpostkit import Client, Endpoint, Endpoints
from outpostkit.utils import convert_outpost_date_str_to_date
from rich.table import Table

from outpostcli.exceptions import SourceNotSupportedError
from outpostcli.utils import (
    add_options,
    api_token_opt,
    click_group,
    combine_inf_load_source_model,
    console,
    entity_opt,
)


@click_group()
def endpoints():
    """
    Manage Endpoints
    """
    pass


@endpoints.command(name="list")
@add_options([api_token_opt, entity_opt])
def list_endpoints(api_token, entity):
    client = Client(api_token=api_token)
    infs_resp = Endpoints(client=client, entity=entity).list()
    inf_table = Table(
        title=f"Endpoints ({infs_resp.total})",
    )
    # "primary_endpoint",
    inf_table.add_column("name")
    inf_table.add_column("model")
    inf_table.add_column("status")
    inf_table.add_column("hardware_instance")
    inf_table.add_column("visibility")
    inf_table.add_column("updated_at", justify="right")
    for inf in infs_resp.endpoints:
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


@endpoints.command(name="create")
@click.argument("model-data", type=str, nargs=1, required=False)
@click.option(
    "--name",
    "-n",
    type=str,
    default=None,
    required=False,
    help="name of the endpoint to create.",
)
@click.option(
    "--huggingface-token-id",
    type=str,
    default=None,
    required=False,
    help="revision of the model to use.",
)
@click.option(
    "--huggingface-token-id",
    type=str,
    default=None,
    required=False,
    help="revision of the model to use.",
)
@click.option(
    "--hardware-instance",
    "-h",
    type=str,
    required=True,
    help="hardware instance type to use",
)
@click.option(
    "--template-path",
    "-p",
    type=str,
    help="template path",
    required=False,
)
@click.option(
    "--task-type",
    "-t",
    type=str,
    default="custom",
    help="task type",
    required=False,
)
@click.option(
    "--base-image",
    type=click.Choice(
        [
            "transformers-pt",
            "transformers-tf",
            "python",
            "diffusers-pt",
            "diffusers-tf",
            "tensorflow",
            "diffusers",
        ]
    ),
    # type=str,
    help="base image",
    required=False,
)
@click.option(
    "--visibility",
    type=click.Choice(["private", "public", "internal"]),
    # type=str,
    help="visibility of the endpoint",
    required=False,
)
@click.option(
    "--replica-scaling-min",
    type=int,
    default=0,
    help="minimum number of replicas",
    required=False,
)
@click.option(
    "--replica-scaling-max",
    type=int,
    default=1,
    help="maximum number of replicas",
    required=False,
)
@click.option(
    "--replica-scaling-scaledown-period",
    type=int,
    default=900,
    help="number of seconds to wait before scaling down.",
    required=False,
)
@click.option(
    "--replica-scaling-target-pending-req",
    type=int,
    default=20,
    help="threshold of number of requests in pending before scaling up.",
    required=False,
)
@add_options([api_token_opt, entity_opt])
def create_endpoint(
    api_token: str,
    entity: str,
    model_data: Optional[str],
    hardware_instance: str,
    huggingface_token_id,
    base_image: Optional[str],
    name: Optional[str],
    template_path: Optional[str],
    task_type: str,
    replica_scaling_min: int,
    replica_scaling_max: int,
    visibility: str,
    replica_scaling_scaledowm_period: int,
    replica_scaling_target_pending_req: int,
):
    client = Client(api_token=api_token)
    if template_path:
        [actual_path, class_name] = template_path.rsplit(":", 1)
        click.echo(f"{actual_path},{class_name}")
        if not actual_path or not class_name:
            click.echo(
                "Please specify the template classname along with the path.", err=True
            )
            return
        if not base_image:
            click.echo("Please specify the base image you want to use.", err=True)
            return
        try:
            result = urlparse(actual_path)
            if all([result.scheme, result.netloc]):
                click.echo("url")
                data = {
                    "templateType": "custom",
                    "customTemplateConfig": {
                        "className": class_name,
                        "url": actual_path,
                    },
                    "hardwareInstance": hardware_instance,
                    "taskType": task_type,
                    "name": name,
                    "containerType": "prebuilt",
                    "visibility": visibility,
                    "prebuiltImageName": base_image,
                    "replicaScalingConfig": {
                        "min": replica_scaling_min,
                        "max": replica_scaling_max,
                        "scaledownPeriod": replica_scaling_scaledowm_period,
                        "targetPendingRequests": replica_scaling_target_pending_req,
                    },
                }
                create_resp = Endpoints(client=client, entity=entity).create(json=data)
            else:
                raise ValueError("Not an url.")
        except ValueError:
            if os.path.exists(actual_path) and os.path.isfile(actual_path):
                click.echo("file")
                # do something
                data = {
                    "templateType": "custom",
                    "customTemplateConfig": {
                        "className": class_name,
                    },
                    "taskType": task_type,
                    "name": name,
                    "containerType": "prebuilt",
                    "visibility": visibility,
                    "hardwareInstance": hardware_instance,
                    "prebuiltImageName": base_image,
                    "replicaScalingConfig": {
                        "min": replica_scaling_min,
                        "max": replica_scaling_max,
                        "scaledownPeriod": replica_scaling_scaledowm_period,
                        "targetPendingRequests": replica_scaling_target_pending_req,
                    },
                }
                create_resp = Endpoints(client=client, entity=entity).create(
                    data={"metadata": json.dumps(data)},
                    files={"template": open(actual_path, mode="rb")},
                )
            else:
                click.echo("Invalid template file path.", err=True)
                return
        except Exception as e:
            click.echo(f"could not parse the template, error: {e}", err=True)
            return
    else:
        # do the other thing
        if not model_data:
            click.echo("Please provided the model name.", err=True)
            return
        m_splits = model_data.split(":", 1)
        model_details: dict[str] = None
        if len(m_splits) == 1:
            [model_name, revision] = model_data.split("@", 1)
            model_details = {
                "modelSource": "outpost",
                "outpostModel": {"fullName": model_name, "commit": revision},
            }
        else:
            if m_splits[0] == "hf" or m_splits[0] == "huggingface":
                [model_name, revision] = model_data.split("@", 1)
                model_details = {
                    "modelSource": "huggingface",
                    "huggingfaceModel": {
                        "id": model_name,
                        "revision": revision,
                        "keyId": huggingface_token_id,
                    },
                }
            else:
                raise SourceNotSupportedError(f"source {m_splits[0]} not supported.")

        create_body = {
            "templateType": "autogenerated",
            "autogeneratedTemplateConfig": model_details,
            "hardwareInstance": hardware_instance,
            "visibility": visibility,
            "name": name,
            "replicaScalingConfig": {
                "min": replica_scaling_min,
                "max": replica_scaling_max,
                "scaledownPeriod": replica_scaling_scaledowm_period,
                "targetPendingRequests": replica_scaling_target_pending_req,
            },
        }
        create_resp = Endpoints(client=client, entity=entity).create(json=create_body)
        click.echo("endpoint created...")
    click.echo(f"name: {create_resp.name}")
    click.echo(f"id: {create_resp.id}")


@endpoints.command("get")
@add_options([api_token_opt, entity_opt])
@click.argument("name", type=str, nargs=1)
def get_endpoint(api_token, entity, name):
    client = Client(api_token=api_token)
    inf_data = Endpoint(client=client, name=name, entity=entity).get()
    click.echo(inf_data.__dict__)


@endpoints.command(name="deploy")
@click.argument("name", type=str, nargs=1)
@add_options([api_token_opt, entity_opt])
def deploy_endpoint(api_token, entity, name):
    client = Client(api_token=api_token)
    deploy_data = Endpoint(client=client, name=name, entity=entity).deploy({})
    click.echo(f"Deployment successful. id: {deploy_data.id}")


@endpoints.command(name="deployments")
@add_options([api_token_opt, entity_opt])
@click.argument("name", type=str, nargs=1)
def list_endpoint_deployments(api_token, entity, name):
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


@endpoints.command(name="delete")
@click.argument("name", type=str, nargs=1)
@add_options([api_token_opt, entity_opt])
def delete_endpoint(api_token, entity, name):
    fullName = f"{entity}/{name}"
    if click.confirm(
        f"do you really want to delete this endpoint: {fullName} ?", abort=True
    ):
        client = Client(api_token=api_token)
        delete_resp = Endpoint(client=client, name=name, entity=entity).delete()
        return "endpoint deleted."

    return "Aborted"


@endpoints.command(name="status")
@click.argument("name", type=str, nargs=1)
@add_options([api_token_opt, entity_opt])
@click.option("--verbose", "-v", is_flag=True, help="Verbose")
def inf_dep_status(api_token, entity, name):
    client = Client(api_token=api_token)
    status_data = Endpoint(
        client=client, api_token=api_token, name=name, entity=entity
    ).status()
    click.echo(status_data)
