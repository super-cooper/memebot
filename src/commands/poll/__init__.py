import asyncio
import datetime
import threading
from string import ascii_lowercase as alphabet
from typing import List

import discord

from commands import Command, CommandOutput
from lib import constants


class Poll(Command):
    """
    Poll command for creating a simple, reaction-based poll.
    """

    def __init__(self):
        super().__init__("poll", "Create a simple poll.", "\"question\" \"ans1\" \"ans2\" ... \"ansN\"")
        self.reactions: List[str] = []
        self.lock = threading.Lock()

    def help_text(self) -> CommandOutput:
        return CommandOutput().set_text(
            "Create a simple poll with a question and multiple answers.\n"
            "If no answers are provided, :thumbsup: and :thumbsdown: will be used.")

    async def exec(self, args: List[str], message: discord.Message) -> 'CommandOutput':
        if len(args) < 1:
            return self.fail("_Missing question argument!_")

        question, *options = args
        embed = discord.Embed(
            title=':bar_chart: **New Poll!**',
            description=f'_{question}_',
            color=constants.COLOR,
            timestamp=datetime.datetime.utcnow()
        )

        # Normally, this lock is only released in the command's callback. If sending the message fails, the callback
        # won't be called.
        # This lock timeout is to prevent permanent lock contention if sending the message fails.
        if not self.lock.acquire(timeout=30):
            raise RuntimeError("Could not acquire lock on poll command!")
        if len(options) == 1:
            return self.fail(f"_Only 1 choice provided. !{self.name} requires either 0 or 2+ choices!_")
        if len(options) == 0 or options in (['yes', 'no'], ['no', 'yes'], ['yea', 'nay'], ['nay', 'yea']):
            embed.add_field(name=':thumbsup:', value=':)').add_field(
                name=':thumbsdown:', value=':(')
            self.reactions = [':thumbsup:', ':thumbsdown:']
        else:
            for i in range(len(options)):
                emoji = f':regional_indicator_{alphabet[i]}:'
                embed.add_field(name=emoji, value=options[i])
                self.reactions.append(emoji)

        return CommandOutput().add_embed(embed)

    async def callback(self, message: discord.Message) -> None:
        for emote in self.reactions:
            asyncio.create_task(message.add_reaction(constants.EMOJI_MAP[emote]))
        self.reactions.clear()
        self.lock.release()
