import shlex

import discord

from commands import Commands


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

        command, *args = shlex.split(message.content)

        if command.startswith('!'):
            # fetch the command function from the commands dict, and execute it with args
            output = Commands.commands()[command](args)
            is_embed = type(output) is discord.Embed
            await message.channel.send(output if not is_embed else None, embed=output if is_embed else None)