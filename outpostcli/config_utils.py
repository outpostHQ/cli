import configparser
import os

from outpostcli.exceptions import NotLoggedInError

CONFIG_FILE = os.environ.get(
    "OUTPOSTCLI_CFG_PATH", os.path.join(os.path.expanduser("~"), ".outpostcli.cfg")
)

config = configparser.ConfigParser()


def write_details_to_config_file(api_key: str, name: str):
    config.read(CONFIG_FILE)
    if "DEFAULT" not in config:
        config["DEFAULT"] = {}
    config["DEFAULT"]["API_TOKEN"] = api_key
    config["DEFAULT"]["ENTITY"] = name
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)


def purge_config_file():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    else:
        raise FileNotFoundError("Config file does not exist.")


def remove_details_from_config_file():
    config.read(CONFIG_FILE)
    api_token = config["DEFAULT"].get("API_TOKEN")
    entity = config["DEFAULT"].get("ENTITY")
    if entity:
        del config["DEFAULT"]["ENTITY"]
    if api_token:
        del config["DEFAULT"]["API_TOKEN"]
        with open(CONFIG_FILE, "w") as configfile:
            config.write(configfile)
    else:
        raise NotLoggedInError()


def get_default_api_token_from_config():
    config.read(CONFIG_FILE)
    return config["DEFAULT"].get("API_TOKEN")


def get_default_entity_from_config():
    config.read(CONFIG_FILE)
    return config["DEFAULT"].get("ENTITY")
