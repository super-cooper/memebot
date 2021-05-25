from typing import List

import discord

from commands import Command, CommandOutput, registry
from commands.registry import top_level_command_registry


class Help(Command):
    """
    Output general help text for each command.
    """

    def __init__(self):
        super().__init__("help", "Learn how to use MemeBot", "[command_name]")

    def long_description(self) -> CommandOutput:
        return CommandOutput(
            content="If no arguments are given, prints a short description of each command known by MemeBot.\n"
                    "If given the name of a command, MemeBot will show more detailed information about that command.")

    async def exec(self, args: List[str], message: discord.Message) -> CommandOutput:
        """
        Prints general help text for all messages
        :param args: ignored
        :param message: Ignored
        :return: A rundown of all of Memebot's commands.
        """
        if args:
            # Prepend a bang to the first arg if not already provided
            cmd_path = args.copy()
            if not cmd_path[0].startswith('!'):
                cmd_path[0] = '!' + cmd_path[0]
            try:
                # Attempt to find the command the user is asking for
                command, _ = registry.parse_command_and_args(list(map(lambda arg: arg.lower(), cmd_path)))
            except ValueError:
                return self.fail(f"Unrecognized command `!{''.join(cmd_path)}`")
            return command.help_text()
        else:
            return CommandOutput().set_text("Commands:\n\t\t" + '\n\t\t'.join(
                f"`!{cmd_name:5}` - {top_level_command_registry[cmd_name].command.description}" for cmd_name in
                sorted(top_level_command_registry)))
