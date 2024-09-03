from collections import OrderedDict
from datetime import datetime
from typing import Optional, Union, Any

import discord
import discord.ext.commands
import emoji

from memebot.lib import constants, exception


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

    buttons = [
        discord.PartialEmoji(name=chr(ord("🇦") + i)) for i in range(len(choices))
    ]
    yes_no = False
    if len(choices) == 1:
        raise exception.MemebotUserError(
            f"_Only 1 choice provided. {interaction.command.qualified_name} "
            f"requires either 0 or 2+ choices!_"
        )
    elif len(choices) == 0 or [c.lower() for c in choices] in (
        ["yes", "no"],
        ["no", "yes"],
        ["yea", "nay"],
        ["nay", "yea"],
    ):
        choices = [emoji.emojize(":thumbs_up:"), emoji.emojize(":thumbs_down:")]
        yes_no = True

    votes = PollResult(question, yes_no, choices)

    vote_view = PollView(timeout=60 * 60 * 24)  # Timeout 1 day
    for i, choice in enumerate(votes.votes):
        vote_view.add_item(
            VoteButton(
                results=votes,
                value=choice,
                label=None if yes_no else choice,
                emoji=choice if yes_no else buttons[i],
            )
        )

    await interaction.response.send_message(embed=votes.to_embed(), view=vote_view)


class PollResult:
    question: str
    yes_no: bool
    votes: OrderedDict[str, list[Union[discord.User, discord.Member]]]

    def __init__(self, question: str, yes_no: bool, options: list[str]):
        self.question = question
        self.votes = OrderedDict()
        self.yes_no = yes_no
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
            voter_names = (x.display_name for x in voters)
            choice_title = f"{choice} ({len(voters)})"
            if not self.yes_no:
                choice_title = f'{chr(ord("🇦") + i)} ' + choice_title

            embed.add_field(
                name=choice_title,
                value="\n".join(voter_names),
            )

        return embed


class PollView(discord.ui.View):
    async def on_timeout(self) -> None:
        for button in self.children:
            if not isinstance(button, discord.ui.Button):
                raise exception.MemebotInternalError(
                    "Non-button found in PollView children"
                )
            button.disabled = True


class VoteButton(discord.ui.Button):
    results: PollResult
    value: str

    def __init__(self, results: PollResult, value: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.results = results
        self.value = value

    async def callback(self, interaction: discord.Interaction) -> None:
        if not self.value:
            raise exception.MemebotInternalError("No value for poll button")
        self.results.vote(self.value, interaction.user)
        await interaction.response.edit_message(embed=self.results.to_embed())
