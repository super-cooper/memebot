import discord

from memebot.integrations import clear_urls
from memebot.lib import exception, util


@discord.app_commands.command()
async def trackers(interaction: discord.Interaction, link: str) -> None:
    """
    Generate the given link without tracking metadata
    """
    if not util.is_url(link):
        raise exception.MemebotUserError("Invalid link")

    await interaction.response.defer(thinking=True)

    await interaction.followup.send(
        f"Link without trackers: {clear_urls.strip_trackers(link)}"
    )


@discord.app_commands.context_menu(name="Remove trackers")
async def trackers_context_menu(
    interaction: discord.Interaction, message: discord.Message
) -> None:
    link = util.extract_link(message)

    await interaction.response.defer(thinking=True)

    await interaction.followup.send(
        f"Link without trackers: {clear_urls.strip_trackers(link)}"
    )
