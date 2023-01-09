from datetime import datetime
from typing import Optional

import discord
import discord.ext.commands
import emoji

from lib import constants, exception


@discord.app_commands.command(
    description="Create a simple poll with a question and multiple answers."
)
async def poll(
    interaction: discord.Interaction,
    question: str,
    choice1: Optional[str],
    choice2: Optional[str],
    choice3: Optional[str],
    choice4: Optional[str],
    choice5: Optional[str],
) -> None:
    """
    Poll command for creating a simple, reaction-based poll.
    """
    if not interaction.command:
        raise exception.MemebotInternalError("Cannot get command from context")
    embed = discord.Embed(
        title=":bar_chart: **New Poll!**",
        description=f"_{question}_",
        color=constants.COLOR,
        timestamp=datetime.utcnow(),
    )
    optional_choices = [choice1, choice2, choice3, choice4, choice5]
    choices = list(filter(None, optional_choices))

    if len(choices) == 1:
        raise exception.MemebotUserError(
            f"_Only 1 choice provided. {interaction.command.qualified_name} requires either 0 or 2+ choices!_"
        )
    elif len(choices) == 0 or [c.lower() for c in choices] in (
        ["yes", "no"],
        ["no", "yes"],
        ["yea", "nay"],
        ["nay", "yea"],
    ):
        embed.add_field(name=":thumbs_up:", value=":)").add_field(
            name=":thumbs_down:", value=":("
        )
        reactions = [":thumbs_up:", ":thumbs_down:"]
    else:
        reactions = []
        for i, choice in enumerate(choices):
            letter_emoji = chr(
                ord("🇦") + i
            )  # emoji does not support regional indicators yet
            reactions.append(letter_emoji)
            embed.add_field(name=letter_emoji, value=choice)

    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    for reaction in reactions:
        await message.add_reaction(emoji.emojize(reaction, language="alias"))
