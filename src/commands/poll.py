from datetime import datetime

import discord
import discord.ext.commands
import emoji

from lib import constants, exception


@discord.ext.commands.command(
    brief="Create a simple poll.",
    help=emoji.emojize("Create a simple poll with a question and multiple answers.\n"
                       f"If no answers are provided, :thumbsup: and :thumbsdown: will be used."),
)
async def poll(ctx: discord.ext.commands.Context, question: str, *choices: str) -> None:
    """
    Poll command for creating a simple, reaction-based poll.
    """
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
            ['yes', 'no'], ['no', 'yes'], ['yea', 'nay'], ['nay', 'yea']):
        embed.add_field(name=':thumbs_up:', value=':)').add_field(name=':thumbs_down:', value=':(')
        reactions = [':thumbs_up:', ':thumbs_down:']
    else:
        reactions = []
        for i, choice in enumerate(choices):
            letter_emoji = chr(ord("🇦") + i)  # emoji does not support regional indicators yet
            reactions.append(letter_emoji)
            embed.add_field(name=letter_emoji, value=choice)

    message = await ctx.send(embed=embed)
    for reaction in reactions:
        await message.add_reaction(emoji.emojize(reaction, language="alias"))
