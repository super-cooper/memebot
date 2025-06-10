from typing import cast
import re

import discord

from memebot.lib import exception

URL_REGEX = r"https?://\S+"


@discord.app_commands.command()
async def paywall(interaction: discord.Interaction, link: str) -> None:
    """
    Generate the given link without a paywall. If replying to a message, use
    the link in the replied-to message
    """
    if not re.fullmatch(URL_REGEX, link):
        raise exception.MemebotUserError("Invalid link")

    link = remove_params(link)

    await interaction.response.send_message(
        f"Link without paywall: https://archive.is/newest/{link}"
    )


@discord.app_commands.context_menu(name="Remove paywall")
async def paywall_context_menu(
    interaction: discord.Interaction, message: discord.Message
) -> None:
    link = remove_params(extract_link(message))
    await interaction.response.send_message(
        f"Link without paywall: https://archive.is/newest/{link}"
    )


def extract_link(message: discord.Message) -> str:
    """Extracts a link from the given message's embeds or content"""
    # Try embeds first because it's easier and more reliable.
    for embed in message.embeds:
        if embed.url:
            return embed.url

    # This should return a list of strings:
    # https://docs.python.org/3/library/re.html#re.findall
    for match in re.findall(URL_REGEX, message.content):
        return cast(str, match)

    raise exception.MemebotUserError("Cannot extract link from replied-to message")


def remove_params(url: str) -> str:
    """Remove the pesky query parameters from the given URL"""
    return url.partition("?")[0]
