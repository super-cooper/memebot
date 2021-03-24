from typing import List

import discord

from commands import Command, CommandOutput
from commands.registry import top_level_command_registry


class Help(Command):
    """
    Output general help text for each command.
    """

    def __init__(self):
        super().__init__("help", "Learn how to use MemeBot")

    def help_text(self) -> CommandOutput:
        return CommandOutput().set_text("Runs this command.")

    async def exec(self, args: List[str], message: discord.Message) -> CommandOutput:
        """
        Prints general help text for all messages
        :param args: ignored
        :param message: Ignored
        :return: A rundown of all of Memebot's commands.
        """
        return CommandOutput().set_text("Commands:\n\t\t" + '\n\t\t'.join(
            f"`!{cmd_name:5}` - {top_level_command_registry[cmd_name].command.description}" for cmd_name in
            sorted(top_level_command_registry)))
