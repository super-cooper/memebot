import re
import shlex

import discord

from commands import Commands, SideEffects


class MemeBot(discord.Client):
    """
    The main class that operates MemeBot, and directly controls all listeners
    """

    def __init__(self, **args):
        super().__init__(**args)

    async def on_ready(self) -> None:
        """
        Determines what the bot does as soon as it is logged into discord
        :return: None
        """
        print(f'Logged in as {self.user}')

    async def on_message(self, message: discord.message.Message) -> None:
        """
        Maintains all basic per-message functions of the bot, including extracting and executing !commands and
        updating databases with new data
        :param message: The most recent message sent to the server
        :return: None
        """
        if message.author == self.user:
            # ignore messages sent by this bot (for now)
            return

        if self.is_command(message.content):
            try:
                command, *args = shlex.split(message.content)
            except ValueError as e:
                await message.channel.send('Could not parse command: ' + str(e))
                return

            result = await Commands.execute(command, args, self, message)
            new_message = await message.channel.send(**result.kwargs)
            await SideEffects.borrow(new_message)

    def is_command(self, msg: str) -> bool:
        """Returns True if msg is a command, otherwise returns False."""
        # re.match looks for a match anywhere in msg. Regex matches if first
        # word of msg is ! followed by letters. 
        return bool(re.match(r'^![a-zA-Z]+(\s|$)', msg))
