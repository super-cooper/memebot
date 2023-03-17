from collections import OrderedDict
from datetime import datetime
from typing import Optional, Union

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
        choices = [emoji.emojize(":thumbs_up:"), emoji.emojize(":thumbs_down:")]

    votes = PollResult(question, choices)

    vote_view = PollView(timeout=60 * 60 * 24)  # Timeout 1 day
    for i, choice in enumerate(votes.votes):
        vote_view.add_item(
            VoteButton(
                votes,
                label=choice,
                emoji=discord.PartialEmoji(name=chr(ord("🇦") + i)),
            )
        )

    await interaction.response.send_message(embed=votes.to_embed(), view=vote_view)


class PollResult:
    question: str
    votes: OrderedDict[str, list[Union[discord.User, discord.Member]]]

    def __init__(self, question: str, options: list[str]):
        self.question = question
        self.votes = OrderedDict()
        for option in options:
            self.votes[option] = []

    def vote(self, choice: str, user: Union[discord.User, discord.Member]) -> None:
        if user in self.votes[choice]:
            self.votes[choice].remove(user)
        else:
            self.votes[choice].append(user)

    def to_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f":bar_chart: **New Poll!**",
            description=f"_{self.question}_",
            color=constants.COLOR,
            timestamp=datetime.utcnow(),
        )
        for i, (choice, voters) in enumerate(self.votes.items()):
            voter_names = map(lambda x: x.display_name, voters)
            embed.add_field(
                name=f'{chr(ord("🇦") + i)} {choice} ({len(voters)})',
                value="\n".join(voter_names),
            )

        return embed


class PollView(discord.ui.View):
    async def on_timeout(self) -> None:
        for button in self.children:
            if not isinstance(button, discord.ui.Button):
                continue
            button.disabled = True


class VoteButton(discord.ui.Button):
    votes: PollResult

    def __init__(self, votes: PollResult, **kwargs):
        super().__init__(**kwargs)
        self.votes = votes

    async def callback(self, interaction: discord.Interaction) -> None:
        if not self.label:
            return
        self.votes.vote(self.label, interaction.user)
        await interaction.response.edit_message(embed=self.votes.to_embed())
