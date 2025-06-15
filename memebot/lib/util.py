import re
from typing import Tuple, List, Optional, cast, get_origin, get_args, Union, Any

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


def is_spoil(message: str, idx: int) -> bool:
    """Returns whether idx of message is within a spoiler text"""
    if idx >= len(message) or idx < 0:
        return False

    # list of tuples of spoil ranges, [start, stop)
    # e.g.: blah blah ||bababababababababab||
    #                   ^start             ^end
    spoil_ranges: List[Tuple[int, int]] = []
    in_spoil = False
    spoil_start = -1
    i = 0
    while i < len(message):
        c = message[i]
        if c == "\\" and not in_spoil:
            # ignore backslashes only for the start of the spoiler
            i += 1
        elif c == "|":
            if i + 1 < len(message) and message[i + 1] == "|":
                if in_spoil:
                    # reached the end of a spoiled section
                    spoil_ranges.append((spoil_start, i))
                else:
                    # start of spoil section
                    spoil_start = i + 2

                i += 1
                in_spoil = not in_spoil

        i += 1

    for start, end in spoil_ranges:
        if start <= idx < end:
            return True
    return False


def maybe_make_link_spoiler(message: str, spoil: bool) -> str:
    """Returns message maybe wrapped in spoiler tags."""
    # Discord will only embed links with spoilers if there is padding
    # between the spoiler tags and the link.
    return f"|| {message} ||" if spoil else message


def parse_invocation(interaction: discord.Interaction) -> str:
    """Returns the command involacion parsed from the raw interaction data"""

    def impl(data: dict) -> str:
        out = []
        name: Optional[str] = data.get("name")
        options: list[dict] = data.get("options", [])
        value: Optional[str] = data.get("value")
        if value:
            out.append(value)
        elif name:
            out.append(name)
        for option in options:
            out.append(impl(option))

        return " ".join(out)

    if not interaction:
        return ""

    if interaction.command:
        prefix = cast(discord.ext.commands.Bot, interaction.client).command_prefix
    else:
        prefix = ""
    return f"{prefix}{impl(cast(dict, interaction.data))}"


def validate_type(data: Any, expected_type: type) -> bool:
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
