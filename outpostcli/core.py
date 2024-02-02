from .config_utils import (
    get_default_api_token_from_config,
    get_default_entity_from_config,
)


def get_api_token(ctx, param, value):
    if value is None:
        return get_default_api_token_from_config()
    else:
        return value


def get_entity(ctx, param, value):
    if value is None:
        return get_default_entity_from_config()
    else:
        return value
