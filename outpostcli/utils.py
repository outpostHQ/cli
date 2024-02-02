from typing import Optional
import click
from rich.console import Console
from outpostkit.inference import InferenceOutpostModel, InferenceHuggingfaceModel


console = Console(highlight=False)


def click_group(*args, **kwargs):
    class ClickAliasedGroup(click.Group):
        def get_command(self, ctx, cmd_name):
            rv = click.Group.get_command(self, ctx, cmd_name)
            if rv is not None:
                return rv

            def is_abbrev(x, y):
                # first char must match
                if x[0] != y[0]:
                    return False
                it = iter(y)
                return all(any(c == ch for c in it) for ch in x)

            matches = [x for x in self.list_commands(ctx) if is_abbrev(cmd_name, x)]

            if not matches:
                return None
            elif len(matches) == 1:
                return click.Group.get_command(self, ctx, matches[0])
            ctx.fail(f"'{cmd_name}' is ambiguous: {', '.join(sorted(matches))}")

        def resolve_command(self, ctx, args):
            # always return the full command name
            _, cmd, args = super().resolve_command(ctx, args)
            return cmd.name, cmd, args

    return click.group(*args, cls=ClickAliasedGroup, **kwargs)


def check_token(token: str):
    from outpostkit import Client

    client = Client(api_token=token)

    try:
        user = client.user
        return 1, user
    except Exception as e:
        click.echo(e)
        return -1, None


def combine_inf_load_source_model(
    load_source,
    outpost_model: Optional[InferenceOutpostModel],
    hf_model: Optional[InferenceHuggingfaceModel],
):
    if load_source == "hugginface" and hf_model:
        return f"hf:{hf_model.id}"
    elif load_source == "outpost" and outpost_model:
        return f"{outpost_model.model.fullName}"
    else:
        return "custom"
