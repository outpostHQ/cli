from typing import Optional

import click
import outpostkit
from outpostkit import Client, Endpoint
from outpostkit.exceptions import OutpostError, OutpostHTTPException

from .config_utils import (
    purge_config_file,
    remove_details_from_config_file,
    write_details_to_config_file,
)
from .constants import cli_version
from .endpoints import endpoints
from .exceptions import NotLoggedInError
from .utils import add_options, api_token_opt, check_token, click_group, entity_opt

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.version_option(cli_version, "-v", "--version")
@click_group(context_settings=CONTEXT_SETTINGS)
def outpostcli():
    pass


# # Add subcommands
outpostcli.add_command(endpoints)


@outpostcli.command()
@add_options([api_token_opt])
def login(api_token: str):
    """
    Login to the outpost.
    """
    (is_logged_in, entity) = check_token(api_token)
    if is_logged_in == 1:
        write_details_to_config_file(api_token, entity.name)
        click.echo("Logged in successfully.")
        click.echo(f"Default namespace: {entity.name}")
    else:
        click.echo("Failed to log in.", err=True)


@outpostcli.command()
@add_options([api_token_opt])
def user(api_token):
    """
    Get details about the currently logged in user.
    """
    click.echo(Client(api_token=api_token).user)
    # click.echo(json.dumps(Client(api_token=api_token).user, indent=4))


@outpostcli.command(name="sdk-version")
def sdk_version():
    """
    Get details about the currently logged in user.
    """
    click.echo(outpostkit.__version__)


@outpostcli.command()
@click.option("--purge", is_flag=True, help="Purge the config file of the login info.")
def logout(purge: bool):  # noqa: FBT001
    """
    Logout of the outpost.
    """
    if purge:
        try:
            purge_config_file()
            click.echo("Logged out successfully.")
        except FileNotFoundError:
            click.echo("No config file found.")
    else:
        try:
            remove_details_from_config_file()
            click.echo("Logged out successfully.")
        except NotLoggedInError:
            click.echo("No logged in user found.")


@outpostcli.command()
@add_options([api_token_opt, entity_opt])
@click.argument("name", type=str, nargs=1)
@click.option("--json-payload", "-j", type=str, help="json payload")
@click.option("--file-payload", "-f", type=str, help="file payload")
@click.option("--data-payload", "-d", type=str, help="form data payload")
@click.option("--query-params", "-q", type=str, help="query params")
@click.option("--headers", "-h", type=str, help="headers")
def predict(
    name: str,
    api_token: str,
    entity: str,
    data_payload: Optional[str],
    file_payload: Optional[str],
    json_payload: Optional[str],
    query_params: Optional[str],
    headers: Optional[str],
):
    """
    get prediction from endpoint
    """
    client = Client(api_token=api_token)
    predictor = Endpoint(client=client, entity=entity, name=name).get_predictor()
    click.echo(predictor.healthcheck())


def outpost():
    try:
        outpostcli()
    except OutpostError as error:
        click.echo(f"An error occurred: {error}", err=True)
    except OutpostHTTPException as error:
        click.echo(f"""APIException occurred - {error}""", err=True)
