import re
from collections.abc import Mapping, Sequence
from typing import Union, cast, get_args, get_origin

import discord
import discord.ext.commands

from memebot.lib import exception

URL_REGEX = re.compile(r"https?://\S+")


def is_url(val: str) -> bool:
    return bool(URL_REGEX.fullmatch(val.strip()))


def extract_link(message: discord.Message) -> str:
    """Extracts a link from the given message's embeds or content"""
    # Try embeds first because it's easier and more reliable.
    for embed in message.embeds:
        if embed.url:
            return embed.url

    # This should return a list of strings:
    # https://docs.python.org/3/library/re.html#re.findall
    for match in URL_REGEX.findall(message.content):
        return cast(str, match)

    raise exception.MemebotUserError("Cannot extract link from replied-to message")


def parse_invocation(interaction: discord.Interaction) -> str:
    """Returns the command invocation parsed from the raw interaction data"""

    def impl(data: Mapping[str, object]) -> str:
        out = []
        name = data.get("name")
        options = data.get("options", [])
        value = data.get("value")
        if value:
            out.append(value)
        elif name:
            out.append(name)
        if type(options) is Sequence[Mapping[str, object]]:
            for option in options:
                out.append(impl(option))

        return " ".join(str(x) for x in out)

    if not interaction or not interaction.data:
        return ""

    if interaction.command:
        prefix = cast(discord.ext.commands.Bot, interaction.client).command_prefix
    else:
        prefix = ""
    return f"{prefix}{impl(interaction.data)}"


def validate_type(data: object, expected_type: type) -> bool:
    """
    Validates that given data matches an expected type. This is useful for
    validation against raw input for which type annotations cannot guarantee
    static correctness.
    """
    origin = get_origin(expected_type)
    args = get_args(expected_type)

    if origin is Union:
        return any(validate_type(data, arg) for arg in args)

    if origin is list:
        if not isinstance(data, list):
            return False
        [item_type] = args
        return all(validate_type(item, item_type) for item in data)

    if origin is dict:
        key_type, val_type = args
        if not isinstance(data, dict):
            return False
        return all(
            validate_type(k, key_type) and validate_type(v, val_type)
            for k, v in data.items()
        )

    return isinstance(data, expected_type)
