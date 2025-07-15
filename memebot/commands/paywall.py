import discord

from memebot.lib import exception, util


@discord.app_commands.command()
async def paywall(interaction: discord.Interaction, link: str) -> None:
    """
    Generate the given link without a paywall. If replying to a message, use
    the link in the replied-to message
    """
    if not util.is_url(link):
        raise exception.MemebotUserError("Invalid link")

    link = remove_params(link)

    await interaction.response.send_message(
        f"[Link]({link}) without paywall: https://archive.is/newest/{link}"
    )


@discord.app_commands.context_menu(name="Remove paywall")
async def paywall_context_menu(
    interaction: discord.Interaction, message: discord.Message
) -> None:
    link = remove_params(util.extract_link(message))
    await interaction.response.send_message(
        f"[Link]({link}) without paywall: https://archive.is/newest/{link}"
    )


def remove_params(url: str) -> str:
    """Remove the pesky query parameters from the given URL"""
    return url.partition("?")[0]
