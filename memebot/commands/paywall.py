from typing import Optional
import re

import discord

from memebot import log
from memebot.lib import exception


@discord.app_commands.command()
async def paywall(interaction: discord.Interaction, link: str) -> None:
    """
    Generate the given link without a paywall. If replying to a message, use
    the link in the replied-to message
    """
    await interaction.response.send_message(
        f"Link without paywall: https://archive.is/newest/{link}"
    )


@discord.app_commands.context_menu(name="paywall")
async def paywall_context_menu(
    interaction: discord.Interaction, message: discord.Message
) -> None:
    link = extract_link(message)
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
    for match in re.findall(r"https?://\S+", message.content):
        return match

    raise exception.MemebotUserError("Cannot extract link from replied-to message")
