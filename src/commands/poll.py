from datetime import datetime
from string import ascii_lowercase as alphabet

import discord
import discord.ext.commands

from lib import constants, exception


@discord.ext.commands.command(
    brief="Create a simple poll.",
    help="Create a simple poll with a question and multiple answers.\n"
    f"If no answers are provided, {constants.EMOJI_MAP[':thumbsup:']} and "
    f"{constants.EMOJI_MAP[':thumbsdown:']} will be used.",
)
async def poll(ctx: discord.ext.commands.Context, question: str, *choices: str) -> None:
    """
    Poll command for creating a simple, reaction-based poll.
    """
    if not ctx.command:
        raise exception.MemebotInternalError("Cannot get command from context")
    embed = discord.Embed(
        title=":bar_chart: **New Poll!**",
        description=f"_{question}_",
        color=constants.COLOR,
        timestamp=datetime.utcnow(),
    )

    if len(choices) == 1:
        raise exception.MemebotUserError(
            f"_Only 1 choice provided. {ctx.command.qualified_name} requires either 0 or 2+ choices!_"
        )
    elif len(choices) == 0 or [c.lower() for c in choices] in (
        ["yes", "no"],
        ["no", "yes"],
        ["yea", "nay"],
        ["nay", "yea"],
    ):
        embed.add_field(name=":thumbsup:", value=":)").add_field(  # type: ignore[attr-defined]
            name=":thumbsdown:", value=":("
        )
        reactions = [":thumbsup:", ":thumbsdown:"]
    else:
        reactions = []
        for i, choice in enumerate(choices):
            emoji = f":regional_indicator_{alphabet[i]}:"
            reactions.append(emoji)
            embed.add_field(name=emoji, value=choice)

    message = await ctx.send(embed=embed)
    for reaction in reactions:
        await message.add_reaction(constants.EMOJI_MAP[reaction])
